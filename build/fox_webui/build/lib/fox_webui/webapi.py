"""Web 层：FastAPI 路由（REST + SSE + 静态托管）。

约定
----
* 只读 StateStore 快照，**不直接调用 ROS**（ROS 调用统一放 control.py）；
* SSE 10Hz 推全量状态（payload 里已剔除 NaN，保证浏览器 JSON.parse 不出错）；
* 静态资源最后 mount 到 "/"，不干扰 /api/* 与 /video/*。
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from fox_webui.video import MJPEG_CT
from fox_webui.peers import http_request

SSE_HZ = 10.0


def sanitize(obj):
    """递归把 NaN/Inf 换成 None：前端 JSON.parse 不接受 NaN 字面量。"""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    return obj


def dumps(obj) -> str:
    return json.dumps(sanitize(obj), ensure_ascii=False, separators=(',', ':'))


def create_app(store, web_dir: str | None = None, extra_status=None,
               broker=None, mapdata=None, control=None, modules=None,
               peers=None) -> FastAPI:
    """构建 FastAPI 应用。

    Args:
        store: StateStore 实例
        web_dir: 前端静态目录（含 index.html）
        extra_status: 可选回调，返回要合并进 /api/state 的额外字段（如任务/控制状态）
        broker: VideoBroker（提供 /video/{color|depth|detect}）
        mapdata: MapData（提供 /api/map 与 /api/map.png）
        control: ControlManager（提供所有控制类接口）
        modules: ProcessManager（提供模块白名单启停接口）
        peers: PeerAggregator（模式 C；提供 /api/robots 与 /api/to/{name}/… 单跳转发）
    """
    app = FastAPI(title='FOX WebUI', version='0.1.0',
                  docs_url='/api/docs', openapi_url='/api/openapi.json')

    def _payload() -> dict:
        snap = store.snapshot()
        if extra_status is not None:
            try:
                extra = extra_status()
                if extra:
                    snap.update(extra)
            except Exception as exc:                      # 额外状态失败不影响主状态
                snap['extra_status_error'] = repr(exc)
        return snap

    @app.get('/api/ping')
    async def api_ping():
        # 全部端点都用 async def：这些操作都是读内存，几微秒完成；
        # 用同步 def 会被丢进线程池，一旦线程池被占满（例如视频流泄漏），
        # 连 /api/ping 都会排队卡死（实测踩过）。
        return {'ok': True, 't': round(time.time(), 3)}

    @app.get('/api/state')
    async def api_state():
        return JSONResponse(_payload())

    @app.get('/api/health')
    async def api_health():
        out = {'ts': round(time.time(), 3), 'topics': store.health()}
        if broker is not None:
            # 视频观看者数量：用于验证"按需订阅"是否生效（无观看者时全为 0）
            out['video_viewers'] = dict(broker.viewers)
        return out

    # ── 视频（按需 MJPEG；无观看者时后端不订阅、不解码）──
    if broker is not None:
        @app.get('/video/{src}')
        async def video(src: str):
            if src not in broker.SOURCES:
                raise HTTPException(404, f'unknown video source: {src}')
            try:
                gen = broker.stream(src)          # 名额在此立即占用（满了踢最旧）
            except RuntimeError as exc:
                raise HTTPException(503, str(exc))
            return StreamingResponse(
                gen, media_type=MJPEG_CT,
                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    # ────────── 控制类接口（全部经 ControlManager → RosDispatcher 走 executor 线程）──────────
    if control is not None:

        async def _body(request: Request) -> dict:
            try:
                return await request.json()
            except Exception:
                return {}

        async def _await_ros(fut, timeout: float = 10.0):
            """等一个 concurrent.futures.Future（由 executor 线程兑现）。"""
            try:
                return await asyncio.wait_for(asyncio.wrap_future(fut), timeout)
            except asyncio.TimeoutError:
                raise HTTPException(504, 'ROS 调用超时（节点可能未启动）')
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                raise HTTPException(500, f'ROS 调用失败: {exc}')

        @app.post('/api/cmd_vel')
        async def api_cmd_vel(request: Request):
            """手动速度指令。⚠️ 必须持续续期（前端 10Hz），300ms 未续期自动归零。"""
            b = await _body(request)
            return control.set_cmd_vel(b.get('vx', 0.0), b.get('vy', 0.0), b.get('vth', 0.0))

        @app.post('/api/estop')
        async def api_estop(request: Request):
            b = await _body(request)
            if b.get('release'):
                return control.estop_release()
            return control.estop(str(b.get('reason', 'webui')))

        @app.get('/api/control')
        async def api_control_status():
            return control.status()

        @app.get('/api/waypoints')
        async def api_waypoints():
            return {'waypoints': control.waypoints, 'nav_home': control.nav_home}

        @app.post('/api/arm/goto')
        async def api_arm_goto(request: Request):
            b = await _body(request)
            return await _await_ros(control.arm_goto(
                float(b.get('x', 0)), float(b.get('y', 0)), float(b.get('z', 0)),
                float(b.get('roll', -1.0))), timeout=30.0)

        @app.post('/api/arm/relative')
        async def api_arm_relative(request: Request):
            b = await _body(request)
            return await _await_ros(control.arm_relative(
                float(b.get('dx', 0)), float(b.get('dy', 0)), float(b.get('dz', 0))),
                timeout=30.0)

        @app.post('/api/arm/home')
        async def api_arm_home():
            return await _await_ros(control.arm_home(), timeout=30.0)

        @app.post('/api/arm/unlock')
        async def api_arm_unlock(request: Request):
            b = await _body(request)
            return await _await_ros(control.arm_unlock(bool(b.get('confirm', False))))

        @app.post('/api/arm/set_zero')
        async def api_arm_set_zero(request: Request):
            b = await _body(request)
            return await _await_ros(control.arm_set_zero(bool(b.get('confirm', False))))

        @app.post('/api/gripper')
        async def api_gripper(request: Request):
            b = await _body(request)
            return await _await_ros(control.gripper(bool(b.get('close', True))))

        @app.post('/api/nav/goal')
        async def api_nav_goal(request: Request):
            b = await _body(request)
            return await _await_ros(control.nav_goal(
                float(b.get('x', 0)), float(b.get('y', 0)), float(b.get('yaw', 0.0))))

        @app.post('/api/nav/cancel')
        async def api_nav_cancel():
            return await _await_ros(control.nav_cancel())

        @app.post('/api/nav/home')
        async def api_nav_home():
            return await _await_ros(control.nav_home())

        @app.post('/api/initial_pose')
        async def api_initial_pose(request: Request):
            """设初始位姿（lidar_loc / AMCL 都需要，否则地图上不会出现机器人）。"""
            b = await _body(request)
            return await _await_ros(control.set_initial_pose(
                float(b.get('x', 0)), float(b.get('y', 0)), float(b.get('yaw', 0.0))))

        # ── 抓取点补偿（实时生效 + 手动保存回 harvest_config.yaml）──
        @app.get('/api/compensation')
        async def api_compensation():
            return control.compensation()

        @app.post('/api/compensation')
        async def api_compensation_set(request: Request):
            """改补偿值。默认只改内存（下一次抓取立即生效）；save=true 才写回配置文件。

            前端步进按钮可以只传增量：{"dx": 5} / {"dy": -1} / {"dz": 10}
            ⚠️ 这几个方法不碰 rclpy（只改内存 dict / 写文件），所以直接同步调用即可，
               不要走 _await_ros（那是给 dispatcher 的 Future 用的）。
            """
            b = await _body(request)
            return control.set_compensation(b, save=bool(b.get('save', False)))

        @app.post('/api/compensation/save')
        async def api_compensation_save():
            """把当前值写回配置文件（保留注释；源码 + install/share 两份都写）。"""
            return control.save_compensation()

        @app.post('/api/compensation/revert')
        async def api_compensation_revert():
            """丢弃未保存改动，回到配置文件里的值。"""
            return control.revert_compensation()

        # ── 采摘任务 ──
        #   start/stop/pause/resume → 发给 harvest_node 的命令话题（整条航点流程）
        #   pick_one             → **WebUI 自己直接驱机械臂**，动作与 scripts/grape_grasp_test.py
        #                         同款（过渡点→抓取点→夹紧→回安全点→松开），
        #                         因此不依赖 harvest 节点是否启动，也不依赖它自己的 YOLO。
        @app.post('/api/task/{action}')
        async def api_task(action: str, request: Request):
            """任务控制：start / stop / pause / resume / pick_one。

            * start    : 跑完整流程（遍历配置航点）
            * pick_one : 只抓一颗；body 带 x/y/z（机器人系 mm，来自检测列表）
            """
            action = str(action).lower()
            if action not in ('start', 'stop', 'pause', 'resume', 'pick_one'):
                raise HTTPException(400, f'不支持的任务动作: {action}')
            b = await _body(request)

            if action == 'pick_one':
                need = [k for k in ('x', 'y', 'z') if b.get(k) is None]
                if need:
                    raise HTTPException(400, f'pick_one 需要 x/y/z 坐标（缺 {need}）')
                # 机械臂动作可能持续十几秒；这里等完整序列（含回安全点+松开）
                return await _await_ros(control.grasp_sequence(
                    float(b['x']), float(b['y']), float(b['z'])), timeout=150.0)

            kw = {}
            res = await _await_ros(control.task_command(action, **kw), timeout=5.0)
            if res.get('subscribers', 0) == 0:
                res['ok'] = False
                res['error'] = '没有节点在听 /grape_harvest/command（先在“模块启停”里启动 harvest）'
            return res

        @app.get('/api/task')
        async def api_task_status():
            snap = store.snapshot()
            cs = control.status()
            return {'task': snap.get('task'), 'listening': cs.get('task_listening'),
                    'running': bool((snap.get('task') or {}).get('running')),
                    'grasping': cs.get('grasping'), 'last_grasp': cs.get('last_grasp')}

    # ── 地图（底图 PNG + 坐标元数据）──
    if mapdata is not None:

        @app.get('/api/map')
        async def api_map():
            return JSONResponse(mapdata.meta())

        @app.get('/api/map.png')
        async def api_map_png():
            data = mapdata.png()
            if data is None:
                raise HTTPException(404, 'map not available')
            return Response(content=data, media_type='image/png',
                            headers={'Cache-Control': 'no-cache'})

    # ── 模块启停（白名单；前端只能传模块名，命令来自 config/modules.yaml）──
    if modules is not None:

        @app.get('/api/modules')
        async def api_modules():
            return modules.status()

        @app.post('/api/modules/{name}/{action}')
        async def api_module_action(name: str, action: str):
            if action == 'start':
                res = modules.start(name)
            elif action == 'stop':
                res = modules.stop(name)
            elif action == 'restart':
                res = modules.restart(name)
            else:
                raise HTTPException(400, f'不支持的动作: {action}（只允许 start/stop/restart）')
            if not res.get('ok'):
                # 用 200 + ok:false 回传，前端统一按 {"ok":..,"error":..} 处理
                return res
            return res

        @app.get('/api/modules/{name}/log')
        async def api_module_log(name: str, limit: int = 200):
            res = modules.logs(name, int(limit))
            if not res.get('ok'):
                raise HTTPException(404, res.get('error', 'unknown module'))
            return res

        @app.post('/api/modules/reload')
        async def api_modules_reload():
            """重新读取 modules.yaml（改配置后不必重启 Agent）。"""
            try:
                modules.load()
            except Exception as exc:
                raise HTTPException(500, f'加载失败: {exc}')
            return {'ok': True, **modules.status()}

    # ── 多机（模式 C：对称 HTTP 聚合）──
    #   本机 Agent 既提供自己的 `/api/...`，也能把请求**单跳**转给邻居 Agent。
    #   这样前端只需记住一个"当前机器"，所有面板统一走 api(path) 即可。
    @app.get('/api/robots')
    async def api_robots():
        """机器清单：本机 + 邻居（含在线状态 / 最后更新延时 / base URL）。"""
        return {'me': (store.snapshot().get('robot') or {}).get('name', ''),
                'robots': store.peers_status()}

    @app.get('/api/map_state')
    async def api_map_state():
        """地图需要的**轻量**状态（pose / scan / plan）。

        为什么单开：MapView 要 2Hz 拿 scan/plan，而**邻居的 scan/plan 不在 SSE 里**
        （紧凑版故意剔除）。若直接拉 `/api/state`，会把 health/modules/control 一起
        拖回来，而且每次都要跑一遍 extra_status —— 这里只取地图要的几个字段。
        """
        snap = store.snapshot()              # ≈0.01 ms，不碰 extra_status
        return JSONResponse({'ts': snap.get('ts'), 'robot': snap.get('robot'),
                             'pose': snap.get('pose'), 'scan': snap.get('scan'),
                             'plan': snap.get('plan')})

    #: 邻居采集只需要这些字段（不含 health/scan/plan/modules —— 又大又用不上）
    _PEER_KEYS = ('ts', 'robot', 'pose', 'twist', 'cmd_vel', 'arm', 'gripper',
                  'battery', 'chassis', 'task', 'control', 'detector')

    @app.get('/api/peer_state')
    async def api_peer_state():
        """模式 C：给邻居采集器用的**轻量**状态端点。

        实测对比：完整 `/api/state` 单机 8.6 KB；本端点 ≈1.7 KB。
        邻居采集 5Hz × 每台 → 跨机流量从 ~43 KB/s 降到 ~8 KB/s（约 5 倍）。
        """
        p = _payload()
        return JSONResponse({k: p.get(k) for k in _PEER_KEYS})

    if peers is not None:
        @app.api_route('/api/to/{name}/{path:path}', methods=['GET', 'POST'])
        async def api_to(name: str, path: str, request: Request):
            """把请求**单跳**转发给邻居 Agent（模式 C）。

            安全护栏（很重要，否则就成了 SSRF / 远程跳板）：
              * 只认 `peers` 名单里**已知的邻居名**（不接受任意主机名/IP）；
              * 只放行 `api/` 前缀的路径（不转发任意 URL）；
              * **不放行 `/api/stream`** —— 那是永不结束的 SSE 流，转发会把
                这个请求按在 `urllib` 里读到超时（实测隐患）；
              * 目标 Agent 收到的是普通 `/api/...`，它**不认识 `/api/to/`**，
                因此不可能 A→B→C 递归 —— 单跳是结构性的，不靠约定。
            """
            base = peers.url_of(name)
            if base is None:
                raise HTTPException(404, f'未知邻居: {name}（只能转发给 peers 名单里的机器）')
            if not path.startswith('api/'):
                raise HTTPException(400, '只允许转发 /api/ 下的路径')
            if path in ('api/stream', 'api/to') or path.startswith('api/to/'):
                raise HTTPException(400, '该路径不支持转发（流式/递归接口请直连）')
            qs = request.url.query or ''
            url = f'{base}/{path}' + (f'?{qs}' if qs else '')
            body = await request.body() if request.method == 'POST' else None
            headers = {'Content-Type': request.headers.get(
                'content-type', 'application/json')}
            try:
                status, hdrs, payload = await asyncio.to_thread(
                    http_request, request.method, url, body, 2.0, headers)
            except Exception as exc:
                raise HTTPException(502, f'邻居 {name} 不可达: {exc}')
            ctype = (hdrs.get('Content-Type') or 'application/json').split(';')[0]
            return Response(content=payload, status_code=status, media_type=ctype)

    @app.get('/api/logs')
    async def api_logs(since: int = 0, limit: int = 200):
        return {'logs': store.logs_since(int(since), int(limit))}

    @app.get('/api/detections')
    async def api_detections():
        """识别结果（由 PreviewDetector 填充；未启用时返回空表）。"""
        if broker is None or broker.detector is None:
            return {'enabled': False, 'detections': []}
        det = broker.detector
        return {'enabled': det.active, 'mode': det.mode,
                'detections': det.snapshot()}

    @app.post('/api/detector')
    async def api_detector_toggle(request: Request):
        """显式启停识别（不带视频观看者时，也能让检测列表出数据）。"""
        if broker is None or broker.detector is None:
            raise HTTPException(503, 'detector not available')
        try:
            body = await request.json()
        except Exception:
            body = {}
        enable = bool(body.get('enable', True))
        if enable:
            broker.detector.acquire()
        else:
            broker.detector.release()
        return {'ok': True, 'status': broker.detector.status()}

    @app.get('/api/stream')
    async def api_stream(request: Request):
        period = 1.0 / SSE_HZ

        async def gen():
            while True:
                if await request.is_disconnected():
                    break
                yield 'data: ' + dumps(_payload()) + '\n\n'
                await asyncio.sleep(period)

        return StreamingResponse(
            gen(), media_type='text/event-stream',
            headers={'Cache-Control': 'no-cache',
                     'Connection': 'keep-alive',
                     'X-Accel-Buffering': 'no'})

    # 静态资源：必须最后 mount（Starlette 按注册顺序匹配）
    if web_dir and os.path.isdir(web_dir):
        app.mount('/', StaticFiles(directory=web_dir, html=True), name='web')
    else:
        @app.get('/')
        def _missing():                                   # pragma: no cover
            return {'error': 'web dir not found', 'web_dir': web_dir}

    return app
