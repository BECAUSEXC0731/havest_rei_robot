"""模块启停（白名单 + 进程组）。

为什么这么写（每一条都是本项目踩过的坑，详见 docs/WebUI_技术文档.md §5.5）
==========================================================================
1. **白名单，不接受命令字符串**：前端只能传模块名，命令来自
   ``config/modules.yaml``。否则等于给了一个免登录的远程 shell。
2. **必须是独立进程组 + killpg**：``ros2 launch`` 自己会派生一堆子进程
   （launch 一个 + 每个 node 一个 + 话题工具……）。只 kill 父 PID 会留下孤儿，
   本项目就因此出现过"ydlidar 没退干净 → 端口被占用 → Unknown error"。
3. **停止先 SIGINT**：``ros2 launch`` 只有收到 SIGINT 才会优雅收尾
   （让各节点正常 destroy、TF/生命周期不留残迹）；SIGTERM/SIGKILL 是超时后的兜底。
4. **不在 shell 里跑**：``Popen(list)`` 不经过 shell，参数里的 ``:=`` 不会被解释，
   也避免注入。子进程环境 = Agent 环境 + ROS 基础路径 + 模块自定义 env。
5. **日志要能看**：每条模块一个读线程把 stdout/stderr 收进环形缓冲，
   前端按模块查看 —— 相当于把终端搬进网页（现场最需要这个）。

线程模型
--------
所有方法都跑在 asyncio 线程（HTTP 处理里），它们**只做 subprocess 与计数器操作**，
不碰任何 rclpy 实体（就绪判据读的是 StateStore 的只读快照），因此没有线程冲突。

⚠️ 性能铁律（2026-10-01 实测定位）
----------------------------------
`status()` 是本项目**最热**的路径：`/api/state` 与 10Hz 的 SSE 每次都调它。
早期实现里它在同步路径上跑 `_refresh_states()`（内部对每个模块 `pgrep` 一次）：

    ProcessManager.status() 一次   = 89 ms   （其中 8 次 pgrep 子进程 = 346 ms）
    × SSE 10Hz                     = 890 ms/秒 → 吃掉 ~89% 的 asyncio 事件循环

后果：**整页卡顿、连 `/api/ping` 都要排队**（事件循环被同步阻塞）。
现在：**状态刷新交给后台 1Hz 线程**，`status()` 只读缓存（≈0.01 ms）；
并且**不再 fork `pgrep`**，改为纯 Python 遍历 `/proc/*/cmdline`（实测 40 ms → ~1 ms）。
"""
from __future__ import annotations

import glob
import os
import signal
import subprocess
import threading
import time
from collections import deque

import yaml

DEFAULT_MODULES_YAML = '/home/ubuntu/ros2fox/src/fox_webui/config/modules.yaml'


def resolve_modules_yaml(explicit: str = '') -> str:
    """定位 modules.yaml：显式参数 > 源码路径 > install/share。"""
    if explicit and os.path.isfile(explicit):
        return explicit
    if os.path.isfile(DEFAULT_MODULES_YAML):
        return DEFAULT_MODULES_YAML
    try:
        from ament_index_python.packages import get_package_share_directory
        cand = os.path.join(get_package_share_directory('fox_webui'), 'config', 'modules.yaml')
        if os.path.isfile(cand):
            return cand
    except Exception:
        pass
    return DEFAULT_MODULES_YAML


# Agent 自身可能已带 ROS 环境；这里再显式补一遍，保证子进程一定能找到 ros2
ROS_PREFIX = '/opt/ros/humble'


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _prepend(env: dict, key: str, values: list[str]) -> None:
    """把 values 拼到 env[key] 前面（去重、保留原有顺序）。"""
    cur = [p for p in (env.get(key) or '').split(':') if p]
    out = [v for v in values if v and v not in cur] + cur
    if out:
        env[key] = ':'.join(out)


def _append(env: dict, key: str, values: list[str]) -> None:
    cur = [p for p in (env.get(key) or '').split(':') if p]
    for v in values:
        if v and v not in cur:
            cur.append(v)
    if cur:
        env[key] = ':'.join(cur)


#: 启动失败的典型日志特征（默认；模块可用 fail_patterns 覆盖/追加）
#:
#: 为什么不只靠就绪判据：像相机这种模块，OrbbecSDK 会在日志里明写
#:   "Command and sensor firmware not createed!" / "No required type sensor found!"
#: 但进程不会退出（它一直在重试），就绪话题也可能被**别的发布者**（如假数据源）
#: 堆上 → 只等超时会给出"启动 30s 仍未就绪"这种没法行动的提示。
#: 直接读日志特征能把真实原因搬给现场。
DEFAULT_FAIL_PATTERNS = [
    'Device initialization failed',
    'No required type sensor found',
    'Caught exception in launch',
    'InvalidFrontendLaunchFileError',
    "KeyError:",
    'error while loading shared libraries',
    'Unable to open port',
    'Permission denied',
    'address already in use',
    'Device or resource busy',
]

#: 命中这些特征时给现场的"怎么办"提示（子串匹配）
HINTS = [
    ('No required type sensor found',
     '深度/IR 传感器没被 SDK 认到（典型：Command and sensor firmware not created）→ '
     '先物理插拔相机；仍然失败就换到 Jetson 的 USB3.0 口（不要经过多级 HUB），最好是带供电的 HUB'),
    ('Device initialization failed',
     '设备初始化 3 次全失败 → 多为 USB 供电/链路问题或设备处于卡死态，插拔一次再试'),
    ('Caught exception in launch',
     'launch 文件加载失败 → 看模块日志里第一条异常（常见：缺环境变量、参数名写错）'),
    ('address already in use',
     '端口/设备被占用 → 先停掉占用方（本项目常见：残留 ydlidar）'),
    ('Unable to open port',
     '串口打不开 → 检查设备是否存在、权限（dialout 组）、是否被其他进程占用'),
]


class ModuleProcess:
    """一个受管模块的运行态。"""

    def __init__(self, name: str, spec: dict):
        self.name = name
        self.spec = spec
        self.proc: subprocess.Popen | None = None
        self.started_at = 0.0
        self.state = 'stopped'          # stopped | starting | running | stopping | failed | external
        self.error = ''
        self.external_pids: list[int] = []   # 不受本进程管理、但看起来就是该模块的进程
        self.logs: deque = deque(maxlen=400)
        self._log_thread: threading.Thread | None = None
        self._log_lock = threading.Lock()

    # ── 日志 ──
    def add_log(self, line: str) -> None:
        with self._log_lock:
            self.logs.append((time.time(), line.rstrip('\n')))

    def tail(self, limit: int = 200) -> list[dict]:
        with self._log_lock:
            items = list(self.logs)[-int(limit):]
        return [{'ts': round(t, 3), 'line': s} for t, s in items]

    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None


class ProcessManager:
    """白名单模块启停管理器。"""

    def __init__(self, store, yaml_path: str = DEFAULT_MODULES_YAML, node=None,
                 refresh_hz: float = 1.0):
        self.store = store
        self.yaml_path = resolve_modules_yaml(yaml_path)
        self.node = node
        self._lock = threading.Lock()
        self._mods: dict[str, ModuleProcess] = {}
        self.workspace = '/home/ubuntu/ros2fox'
        # 话题 → publisher 个数（由 executor 线程的 1Hz timer 刷新）
        self._graph: dict[str, int] = {}
        # ── 状态缓存（性能关键，见文件头与 status() 的说明）──
        self._cache: dict | None = None
        self._cache_ts = 0.0
        self._cache_lock = threading.RLock()
        # ⚠️ TTL 必须 **大于** 刷新周期！
        #    最初写成 0.9 s（小于 1 s 刷新周期）→ 每秒都有 "缓存刚过期、后台线程还没刷"
        #    的窗口，落在窗口里的请求会在**事件循环里同步跑一次 `_rebuild()`**，
        #    实测把 `/api/state` 的 p95 抬到 **1148 ms**、`/api/cmd_vel` 抬到 676 ms
        #    （而 `/api/ping` 仍 < 50 ms —— 一看就知道是“某个接口自带的周期性慢活”）。
        #    这里取 3 个刷新周期；TTL 只当"后台线程挂了"的兜底，不参与正常运行。
        self._refresh_hz = max(0.2, float(refresh_hz))
        self._cache_ttl = max(2.5, 3.0 / self._refresh_hz)
        self._refresher_stop = threading.Event()
        self._refresher: threading.Thread | None = None
        self.load()
        if node is not None:
            # ⚠️ 与其它组件同一铁律：rclpy 调用只在 executor 线程做
            node.create_timer(1.0, self._refresh_graph)
        self._start_refresher()

    # ────────────── 后台刷新（性能关键）──────────────

    def _start_refresher(self) -> None:
        """起一个后台线程，按 `refresh_hz` 重建状态缓存。

        为什么必须异步：见文件头"性能铁律"。刷新只读 StateStore 快照与
        `/proc`，**不碰 rclpy 实体**，所以放普通线程里是安全的。
        """
        if self._refresher is not None:
            return
        self._refresher = threading.Thread(target=self._refresher_loop,
                                           name='webui-modules-refresh', daemon=True)
        self._refresher.start()

    def shutdown(self) -> None:
        self._refresher_stop.set()

    def _refresher_loop(self) -> None:
        period = 1.0 / self._refresh_hz
        while not self._refresher_stop.is_set():
            try:
                self._rebuild()
            except Exception:
                pass            # 刷新失败不影响接口：status() 会自动回退到同步重建
            self._refresher_stop.wait(period)

    def _refresh_graph(self) -> None:
        """在 executor 线程里查 ROS 图：每个 ready 话题现在有几个 publisher。"""
        topics = set()
        for mp in self._mods.values():
            t = (mp.spec.get('ready') or {}).get('topic')
            if t:
                topics.add(str(t))
        out = {}
        for t in topics:
            try:
                out[t] = int(self.node.count_publishers(t))
            except Exception:
                out[t] = 0
        self._graph = out

    # ────────────── 配置 ──────────────

    def load(self) -> None:
        with open(self.yaml_path, 'r', encoding='utf-8') as fp:
            cfg = yaml.safe_load(fp) or {}
        self.workspace = str(cfg.get('workspace') or self.workspace)
        mods = cfg.get('modules') or {}
        with self._lock:
            keep = {}
            for name, spec in mods.items():
                old = self._mods.get(name)
                if old is not None:                 # reload 时保留运行态
                    old.spec = spec
                    keep[name] = old
                else:
                    keep[name] = ModuleProcess(name, spec)
            self._mods = keep
        self._invalidate()

    def names(self) -> list[str]:
        return list(self._mods.keys())

    def _child_env(self, spec: dict) -> dict:
        env = dict(os.environ)
        env.setdefault('ROS_DOMAIN_ID', '0')
        # ⚠️ ROS_DISTRO 等"发行版元信息"必须显式给：很多 launch 文件会直接
        #    `os.environ['ROS_DISTRO']`（例如 orbbec 的 astra_pro_plus.launch.py），
        #    而 Agent 自己是被 fox_webui_env.sh 拉起来的、并不经过 setup.zsh，
        #    少了这几个变量子进程就会以 `KeyError: 'ROS_DISTRO'` 立刻退出（实测踩过）。
        env.setdefault('ROS_DISTRO', 'humble')
        env.setdefault('ROS_VERSION', '2')
        env.setdefault('ROS_PYTHON_VERSION', '3')
        _prepend(env, 'PATH', [os.path.join(ROS_PREFIX, 'bin')])
        _append(env, 'PYTHONPATH', [os.path.join(ROS_PREFIX, 'lib/python3.10/site-packages')])
        _append(env, 'LD_LIBRARY_PATH', [os.path.join(ROS_PREFIX, 'lib')])
        _append(env, 'AMENT_PREFIX_PATH', [ROS_PREFIX])
        _append(env, 'CMAKE_PREFIX_PATH', [ROS_PREFIX])
        for k, v in (spec.get('env') or {}).items():
            env[str(k)] = str(v)
        return env

    # ────────────── 就绪判据 ──────────────

    def _ready_state(self, mp: ModuleProcess) -> dict:
        """返回 {'has_data': bool, 'hz': float}。

        两个来源（互补，都必需）：
        * **ROS 图**：`count_publishers(topic) > 0` —— 能判断“有人发”，对任意话题都有效
          （由 executor 线程的 1Hz timer 刷新，见 _refresh_graph）。
        * **健康频率**：StateStore 里被监控话题的实测 Hz —— 只有监控列表内的话题有。
          为什么不能只靠图：图里“有 publisher”不等于“真的在发数据”
          （节点卡住/挂了但进程还在，图缓存不会立刻清）。
        """
        ready = mp.spec.get('ready') or {}
        topic = ready.get('topic')
        if not topic:
            return {'has_data': mp.alive(), 'hz': None, 'pubs': None}
        topic = str(topic)
        pubs = self._graph.get(topic)
        try:
            h = (self.store.health() or {}).get(topic) or {}
        except Exception:
            h = {}
        # ⚠️ 只有"真的收到过样本"才把频率当作可信依据：
        #    像 /camera/color/image_raw 是**按需订阅**的话题（没人看视频时 agent 不订阅），
        #    健康表里恒为 0Hz —— 若直接拿它比 min_hz，模块会永远卡在"启动中"（实测踩过）。
        hz_known = bool(h.get('count'))
        hz = float(h.get('hz') or 0.0) if hz_known else None

        if ready.get('static'):
            ok = bool(pubs) or bool(h.get('count'))
        elif pubs is not None:
            ok = pubs > 0                     # 主判据：ROS 图里有人发这个话题
            if ok and hz is not None and ready.get('min_hz'):
                ok = bool(h.get('online')) and hz >= float(ready['min_hz'])
        else:
            ok = bool(h.get('online')) and hz is not None and \
                hz >= float(ready.get('min_hz', 0.0))
        return {'has_data': ok, 'hz': hz, 'pubs': pubs}

    def _detect_pattern(self, spec: dict) -> str:
        """推导'如何认出这个模块的进程'（用于发现 Agent 重启后遗留的实例）。

        为什么不直接用整条命令：`pgrep -f` 是正则，`:=` 或空格都可能出问题；
        而 launch 文件名/脚本名足够唯一。模块里可用 `detect:` 显式覆盖。
        """
        pat = spec.get('detect')
        if pat:
            return str(pat)
        for tok in (spec.get('cmd') or []):
            t = str(tok)
            if t.endswith('.launch.py') or t.endswith('.py'):
                return t
        return ''

    def _scan_external(self, mp: ModuleProcess, procs: list | None = None) -> list[int]:
        """找出不受本进程管理、但看起来就是该模块的进程。

        背景：子进程是 `start_new_session=True` 拉起来的（这样停止时能整组发信号），
        代价是 **Agent 重启/崩溃后它们会活着但没人管** —— 界面显示"已停止"，
        用户再点启动就会出现两个实例（实测：restart Agent 后出现 2 个相机实例）。

        ⚠️ 用纯 Python 遍历 `/proc/*/cmdline`，**不 fork `pgrep`**：
        实测 `subprocess.run(['pgrep', ...])` 在本机负载下要 **40 ms**，
        8 个模块就是 320 ms —— 而这段代码会被 status() 高频调用（见文件头“性能铁律”）。
        另外子串匹配比 `pgrep -f` 的正则更精确（`detect` 里的 `.` 不再通配）。

        `procs` 可由调用方传入（一次扫描、多个模块复用），避免 N 个模块扫 N 遍 `/proc`。
        """
        if mp.alive():
            return []
        pat = self._detect_pattern(mp.spec)
        if not pat:
            return []
        if procs is None:
            procs = self._proc_cmdlines()
        return [pid for pid, cmd in procs if pat in cmd]

    @staticmethod
    def _proc_cmdlines() -> list:
        """一次遍历 `/proc`，返回 [(pid, cmdline), …]。

        一轮重建里只需扫一次 `/proc`，再对多个模块做子串匹配即可 ——
        比“每个模块各扫一遍”快 N 倍（实测 `_rebuild()` 33 ms → ~5 ms）。
        """
        me = os.getpid()
        out = []
        for d in glob.glob('/proc/[0-9]*'):
            try:
                pid = int(d.rsplit('/', 1)[-1])
                if pid == me:
                    continue
                with open(os.path.join(d, 'cmdline'), 'rb') as fp:
                    cmd = fp.read().decode('utf-8', 'replace').replace('\0', ' ')
            except Exception:
                continue                      # 进程刚退出 / 无权限 → 跳过
            if cmd:
                out.append((pid, cmd))
        return out

    def _fatal_hit(self, mp: ModuleProcess) -> str:
        """在模块日志尾部找致命特征，返回那行原文（没命中返回空串）。"""
        pats = list(mp.spec.get('fail_patterns') or DEFAULT_FAIL_PATTERNS)
        with mp._log_lock:
            lines = [l for _t, l in list(mp.logs)[-60:]]
        for line in reversed(lines):
            for p in pats:
                if p and p in line:
                    return line.strip()[:200]
        return ''

    @staticmethod
    def _hint_for(line: str) -> str:
        for key, hint in HINTS:
            if key in line:
                return hint
        return ''

    def _refresh_states(self) -> None:
        """把每个模块的运行态推进到最新（由 status() 调用，幂等）。

        ⚠️ `/proc` 每轮只扫一次（懒取）：只有真的需要"找外部实例"时才扫，
        且扫一次给所有模块复用（以前是每个模块各扫一遍）。
        """
        procs = None
        for mp in self._mods.values():
            if mp.state in ('starting', 'running'):
                if not mp.alive():
                    rc = mp.proc.returncode if mp.proc else None
                    mp.state = 'failed'
                    mp.error = f'进程已退出 (code={rc})'
                    mp.add_log(f'[webui] 进程退出 code={rc}')
                    continue
                r = self._ready_state(mp)
                if mp.state == 'starting':
                    if r['has_data']:
                        mp.state = 'running'
                        mp.add_log('[webui] 就绪判据满足 → running')
                    elif time.time() - mp.started_at > 30.0:
                        # 慢启动的模块（相机/导航）可能只是慢，但若日志里已有致命特征
                        # （例如相机设备初始化失败）就直接判失败，别让现场干等
                        hit = self._fatal_hit(mp)
                        if hit:
                            mp.state = 'failed'
                            hint = self._hint_for(hit)
                            mp.error = f'启动失败：{hit}' + (f'\n💡 {hint}' if hint else '')
                        else:
                            mp.error = '启动 30s 仍未满足就绪判据（话题未出现？）'
                continue
            # 不在本进程管理下 → 看是否有遗留实例（Agent 重启后常见）
            if mp.state in ('stopped', 'failed'):
                if procs is None:
                    procs = self._proc_cmdlines()
                ext = self._scan_external(mp, procs)
                mp.external_pids = ext
                if ext:
                    mp.state = 'external'
                    mp.error = f'检测到外部实例: pid {ext}（可能是 Agent 上次退出后遗留的）'

    # ────────────── 启停 ──────────────

    def _missing_deps(self, name: str) -> list[str]:
        spec = self._mods[name].spec
        out = []
        for dep in (spec.get('requires') or []):
            d = self._mods.get(dep)
            if d is None or d.state != 'running':
                out.append(dep)
        return out

    def start(self, name: str) -> dict:
        self._invalidate()     # 状态要变了 → 缓存失效，用户点完立刻看到新状态
        if name not in self._mods:
            return {'ok': False, 'error': f'未知模块: {name}（只允许白名单内的模块）'}
        mp = self._mods[name]
        if mp.alive():
            return {'ok': True, 'message': f'{name} 已在运行', 'state': mp.state}

        # 外部遗留实例（例如 Agent 上次退出后没清的相机）→ 先提醒，不默默再起一个
        ext = self._scan_external(mp)
        if ext:
            mp.external_pids = ext
            mp.state = 'external'
            mp.error = f'检测到外部实例: pid {ext}'
            return {'ok': False, 'state': 'external',
                    'error': (f'已存在 {name} 的实例（pid {ext}）但不受本程序管理：'
                              f'请先点"停止"清掉它，或确认它不需要再启动'),
                    'external_pids': ext}

        missing = self._missing_deps(name)
        if missing:
            return {'ok': False, 'error': f'依赖未启动: {missing}（请先启动它们）',
                    'missing': missing}

        spec = mp.spec
        # 1) 启动前清理（例如 pkill 残留 ydlidar）
        pre = spec.get('pre')
        if pre:
            try:
                r = subprocess.run([str(x) for x in pre], capture_output=True, timeout=8)
                mp.add_log(f'[webui] pre: {" ".join(map(str, pre))} → rc={r.returncode}')
            except Exception as exc:
                mp.add_log(f'[webui] pre 失败(忽略): {exc}')

        # 2) 启动（独立进程组）
        cmd = [str(x) for x in spec.get('cmd') or []]
        if not cmd:
            return {'ok': False, 'error': f'{name} 未配置 cmd'}
        try:
            proc = subprocess.Popen(
                cmd, cwd=str(spec.get('cwd') or self.workspace),
                env=self._child_env(spec),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,          # ⚠️ 独立进程组，停止时 killpg
                bufsize=1, text=True, errors='replace')
        except Exception as exc:
            mp.state = 'failed'
            mp.error = str(exc)
            return {'ok': False, 'error': f'启动失败: {exc}'}

        mp.proc = proc
        mp.state = 'starting'
        mp.started_at = time.time()
        mp.error = ''
        mp.add_log(f'[webui] 已启动 pid={proc.pid}: {" ".join(cmd)}')

        # 3) 日志泵
        def pump() -> None:
            try:
                for line in proc.stdout:            # type: ignore[union-attr]
                    mp.add_log(line)
            except Exception:
                pass
        mp._log_thread = threading.Thread(target=pump, name=f'log-{name}', daemon=True)
        mp._log_thread.start()

        return {'ok': True, 'message': f'{name} 启动中（等就绪判据）', 'pid': proc.pid,
                'state': 'starting'}

    def stop(self, name: str, timeout: float = 3.0) -> dict:
        self._invalidate()     # 同上：状态要变了
        if name not in self._mods:
            return {'ok': False, 'error': f'未知模块: {name}'}
        mp = self._mods[name]

        # 外部遗留实例：用普通 kill（不能 killpg，我们并不拥有它的会话）
        if not mp.alive():
            ext = mp.external_pids or self._scan_external(mp)
            if ext:
                killed = []
                for pid in ext:
                    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
                        if not _pid_alive(pid):
                            break
                        try:
                            os.kill(pid, sig)
                        except ProcessLookupError:
                            break
                        except Exception:
                            break
                        time.sleep(0.4)
                    killed.append(pid)
                left = [p for p in ext if _pid_alive(p)]
                mp.external_pids = left
                mp.state = 'external' if left else 'stopped'
                mp.error = f'仍有外部实例未退出: {left}' if left else ''
                mp.add_log(f'[webui] 清理外部实例 {killed}（剩余 {left}）')
                return {'ok': not left, 'state': mp.state,
                        'message': f'已清理外部实例 {killed}' if not left else f'部分未退出 {left}',
                        'external_killed': killed}
            mp.state = 'stopped'
            return {'ok': True, 'message': f'{name} 未在运行', 'state': 'stopped'}

        mp.state = 'stopping'
        pid = mp.proc.pid                          # type: ignore[union-attr]
        # SIGINT → 3s → SIGTERM → 2s → SIGKILL，全部发给整个进程组
        for sig, wait in ((signal.SIGINT, timeout), (signal.SIGTERM, 2.0),
                          (signal.SIGKILL, 1.0)):
            try:
                os.killpg(os.getpgid(pid), sig)
            except ProcessLookupError:
                break
            except Exception as exc:
                mp.add_log(f'[webui] killpg({sig}) 失败: {exc}')
                break
            try:
                mp.proc.wait(timeout=wait)         # type: ignore[union-attr]
                mp.add_log(f'[webui] 收到信号 {sig.name} 后退出')
                break
            except subprocess.TimeoutExpired:
                mp.add_log(f'[webui] {sig.name} 后 {wait}s 未退出，升级信号')

        rc = mp.proc.returncode if mp.proc else None
        alive = mp.alive()
        mp.state = 'failed' if alive else 'stopped'
        if alive:
            mp.error = '进程未能停止（可能需要手动处理）'
        return {'ok': not alive, 'state': mp.state,
                'message': f'{name} 已停止' if not alive else f'{name} 停止失败',
                'code': rc}

    def restart(self, name: str) -> dict:
        self._invalidate()
        r1 = self.stop(name)
        if not r1.get('ok'):
            return r1
        time.sleep(0.5)
        return self.start(name)

    def stop_all(self) -> dict:
        out = {}
        for name in list(self._mods.keys()):
            out[name] = self.stop(name).get('state')
        return out

    # ────────────── 状态 ──────────────

    def status(self) -> dict:
        """模块状态。**快路径：只读缓存**（≈0.01 ms）。

        这是最热的接口路径，千万不要在这里做同步的进程扫描 —— 见文件头“性能铁律”。
        缓存由后台 1Hz 线程刷新；启停/重载后 `_invalidate()` 会让它立刻失效，
        所以用户点完按钮仍能马上看到新状态。
        """
        with self._cache_lock:
            if self._cache is not None and (time.time() - self._cache_ts) < self._cache_ttl:
                return self._cache
        return self._rebuild()          # 缓存过期（或刚被失效）→ 同步重建一次

    def _rebuild(self) -> dict:
        """重建模块状态缓存（慢路径：只在缓存过期/刚启停过时走）。"""
        self._refresh_states()
        mods = {}
        for name, mp in self._mods.items():
            r = self._ready_state(mp)
            mods[name] = {
                'name': name,
                'desc': mp.spec.get('desc', name),
                'state': mp.state,
                'ready': bool(r['has_data']),
                'hz': round(r['hz'], 2) if r.get('hz') is not None else None,
                'pubs': r.get('pubs'),
                'pid': mp.proc.pid if mp.alive() else None,
                'uptime': round(time.time() - mp.started_at, 1) if mp.started_at and mp.alive() else 0.0,
                'requires': list(mp.spec.get('requires') or []),
                'confirm': bool(mp.spec.get('confirm')),
                'ready_topic': (mp.spec.get('ready') or {}).get('topic'),
                'cmd': ' '.join(str(x) for x in (mp.spec.get('cmd') or [])),
                'error': mp.error,
                'hint': self._hint_for(mp.error or ''),
                'external_pids': list(mp.external_pids),
                'missing': self._missing_deps(name),
            }
        out = {'modules': mods, 'order': self.names(), 'yaml': self.yaml_path}
        with self._cache_lock:
            self._cache = out
            self._cache_ts = time.time()
        return out

    def _invalidate(self) -> None:
        """让状态缓存立刻失效（启停/重载后调用）。"""
        with self._cache_lock:
            self._cache_ts = 0.0

    def logs(self, name: str, limit: int = 200) -> dict:
        if name not in self._mods:
            return {'ok': False, 'error': f'未知模块: {name}'}
        return {'ok': True, 'name': name, 'logs': self._mods[name].tail(limit)}
