"""模式 C（对称 HTTP 聚合）：邻居名单解析 + 状态采集线程 + 极简 HTTP 客户端。

设计要点（详见 docs/WebUI_技术文档.md §5.2 / §7.4）
----------------------------------------------------
* **每个 Agent 进程各跑一份** `PeerAggregator`：按 `peer_hz` 拉邻居的 `GET /api/state`；
* **只拉一层，绝不递归** → 拓扑恒为一层星形，天然防环；
* **只用 HTTP，绝不碰 rclpy** → 与"ROS 实体只能在 executor 线程创建/销毁"（§5.3 铁律）
  无关，因此不会引入跨线程死锁；
* 用 **stdlib `urllib`**，不引入新依赖（现场机器人常无外网，pip 装包不可靠）；
* 邻居掉线只标灰，**绝不影响本机数据与页面**。

为什么 `peers` 是字符串而不是 ROS 数组参数
------------------------------------------------
ROS2 的数组参数 + `ros2 launch` 的引号/转义极易踩坑（本项目已踩过 YAML 参数格式的坑：
`Cannot have a value before ros__parameters`）。字符串格式 `名字=URL` 用逗号分隔，
命令行最好写、最不容易出错：

    peers:="bot2=http://192.168.1.12:8080,bot3=http://192.168.1.13:8080"
"""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

#: 单次 HTTP 响应的最大读取字节数（防止对方返回巨物把内存吃光）
MAX_BYTES = 512 * 1024

#: 从邻居快照里剔除的重字段：不进 SSE（10Hz 推给浏览器，必须轻量）。
#: 需要这些字段时，用 `/api/to/<name>/…` 或 `/api/map_state` 按需单独取。
HEAVY_KEYS = ('scan', 'plan', 'health', 'robots', 'modules')


def parse_peers(spec: str, me: str = '') -> list[dict]:
    """把 `bot2=http://192.168.1.12:8080,bot3=http://…` 解析为 `[{'name','url'}, …]`。

    宽容处理：
      * 分隔符支持逗号 / 分号 / 换行（现场手输时很容易混用）；
      * `name=url` 或只给 `url`（自动用主机名当名字）；
      * 自动补 `http://`、去掉尾部 `/`；
      * 跳过空项、跳过自己（`name == me`）、按名字去重。
    """
    out: list[dict] = []
    seen: set[str] = set()
    if not spec:
        return out
    for raw in str(spec).replace(';', ',').replace('\n', ',').split(','):
        item = raw.strip()
        if not item:
            continue
        if '=' in item:
            name, url = item.split('=', 1)
            name, url = name.strip(), url.strip()
        else:
            url = item
            name = urllib.parse.urlsplit(url if '//' in url else '//' + url).hostname or url
        if not url:
            continue
        if not url.startswith('http'):
            url = 'http://' + url
        url = url.rstrip('/')
        if not name or name == me or name in seen:
            continue
        seen.add(name)
        out.append({'name': name, 'url': url})
    return out


def http_request(method: str, url: str, body=None, timeout: float = 1.0,
                 extra_headers: dict | None = None) -> tuple[int, dict, bytes]:
    """极简 HTTP 客户端（stdlib）。返回 `(status, headers, payload)`。

    * 4xx/5xx **不抛异常**（返回真实状态码 + 响应体），这样转发端点可以原样透传邻居的错误；
    * 真正连不上/超时才抛异常，由调用方决定怎么标灰。
    """
    data = None
    headers = dict(extra_headers or {})
    if body is not None:
        data = body if isinstance(body, (bytes, bytearray)) else json.dumps(body).encode()
        headers.setdefault('Content-Type', 'application/json')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return int(r.status), dict(r.headers), r.read(MAX_BYTES)
    except urllib.error.HTTPError as e:            # 4xx/5xx：透传
        try:
            payload = e.read(MAX_BYTES)
        except Exception:
            payload = b''
        return int(e.code), dict(e.headers or {}), payload or b''


def http_get_json(url: str, timeout: float = 1.0) -> dict:
    """GET 一个 JSON 端点（邻居的 `/api/state`）。"""
    _status, _hdrs, payload = http_request('GET', url, timeout=timeout)
    return json.loads(payload.decode('utf-8', 'replace') or '{}')


class PeerAggregator:
    """邻居状态采集线程（每个 Agent 进程各一份）。

    生命周期：`start()`（登记名单 + 起 daemon 线程）→ `stop()`。
    线程只做两件事：HTTP 拉邻居状态、写入 `StateStore`。**绝不触碰 rclpy**。
    """

    def __init__(self, me: str, peers: list[dict], store,
                 hz: float = 5.0, timeout: float = 1.0):
        self.me = me
        self.peers = list(peers or [])
        self.store = store
        self.hz = max(0.2, float(hz or 5.0))
        self.timeout = max(0.2, float(timeout or 1.0))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        #: name -> {'ok': int, 'fail': int, 'last_ms': float}（仅用于 /api/robots 观测）
        self._stats: dict[str, dict] = {}

    # ── 生命周期 ──
    def start(self) -> None:
        if not self.peers or self._thread is not None:
            return
        self.store.set_peers(self.peers)           # 先把名单登记进快照，UI 立刻能看到
        self._thread = threading.Thread(target=self._run, name='webui-peers', daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def url_of(self, name: str) -> str | None:
        """邻居名 → base URL（供 `/api/to/{name}/…` 转发使用）。"""
        for p in self.peers:
            if p['name'] == name:
                return p['url']
        return None

    # ── 采集循环 ──
    def _run(self) -> None:
        period = 1.0 / self.hz
        while not self._stop.is_set():
            t0 = time.time()
            for p in self.peers:
                if self._stop.is_set():
                    return
                self._poll(p)
            # 扣掉本轮耗时，避免"拉得慢就变慢"的雪崩
            time.sleep(max(0.0, period - (time.time() - t0)))

    def _poll(self, p: dict) -> None:
        name, url = p['name'], p['url']
        st = self._stats.setdefault(name, {'ok': 0, 'fail': 0, 'last_ms': 0.0})
        t0 = time.time()
        try:
            # 优先用对方的**轻量**端点（实测 1.7 KB vs 完整 /api/state 8.6 KB）。
            # 对方是旧版 Agent（没有该端点）时回退到 /api/state，并记住下次别再试。
            legacy = bool(p.get('_legacy'))
            code, _hdrs, payload = http_request(
                'GET', url + ('/api/state' if legacy else '/api/peer_state'),
                timeout=self.timeout)
            if code == 404 and not legacy:
                p['_legacy'] = True
                code, _hdrs, payload = http_request('GET', url + '/api/state',
                                                    timeout=self.timeout)
            if code != 200:
                raise RuntimeError(f'HTTP {code}')
            snap = json.loads(payload.decode('utf-8', 'replace') or '{}')
            for k in HEAVY_KEYS:
                snap.pop(k, None)          # 兼底：旧版端点会把重字段一起带回来
            st['ok'] += 1
            self.store.update_robot(name, snap)
        except Exception as exc:            # 连不上/超时/JSON 坏 → 只标灰
            st['fail'] += 1
            self.store.mark_offline(name, str(exc)[:120])
        st['last_ms'] = round((time.time() - t0) * 1000.0, 1)

    # ── 观测 ──
    def status(self) -> dict:
        return {
            'enabled': bool(self.peers),
            'me': self.me,
            'hz': self.hz,
            'timeout': self.timeout,
            'peers': [dict(p, **self._stats.get(p['name'], {})) for p in self.peers],
        }
