"""控制层：底盘手动 / 机械臂 / 夹爪 / 导航 / 急停。

线程铁律（详见 docs/WebUI_技术文档.md §5.3）
==========================================
rclpy 实体只能在 **executor 线程** 创建/销毁；而 Web 层跑在 asyncio 线程。
所以本模块用两层隔离：

1. ``RosDispatcher``：把"要做的 ROS 调用"投递到一个 50Hz 的 ROS timer（executor 线程）
   里执行，调用方（asyncio）拿到 ``concurrent.futures.Future``，
   用 ``asyncio.wrap_future`` 等结果 → 不阻塞事件循环、也不跨线程碰 rclpy。
2. **速度指令不直接发**：``set_cmd_vel`` 只记录"期望速度 + 时间戳"，
   由 executor 线程里的 10Hz timer 统一发布。这样做一举两得：
   * 发表动作只在一个线程里发生；
   * 天然实现"松手即停"——300ms 没续期就自动归零（看门狗），
     断网/关页面也不会让车一直跑。

安全
----
* ``/unlock``、``/set_zero`` 这类会解除机械臂力/改零点的动作，必须显式二次确认；
* 机械臂工作空间越界在**这里就拦住**，不依赖驱动自身的"螺旋就近修正"；
* 急停是**锁存**的：锁上后所有速度指令被忽略、持续发零，必须显式解除。
"""
from __future__ import annotations

import concurrent.futures
import json
import math
import os
import queue
import threading
import time

import yaml

from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from std_msgs.msg import String
from std_srvs.srv import SetBool

from arm_controller.srv import Move, RelativePos

from fox_webui.compensation import ConfigWriter, KEYS as COMP_KEYS, LIMIT_MM as COMP_LIMIT

try:
    from nav2_msgs.action import NavigateToPose
    _NAV_OK = True
except Exception:                                    # pragma: no cover
    NavigateToPose = None
    _NAV_OK = False


DEFAULT_HARVEST_CFG = '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml'


class RosDispatcher:
    """把 ROS 调用投递到 executor 线程执行的小工具（见模块 docstring）。"""

    def __init__(self, node, hz: float = 50.0):
        self.node = node
        self._q: queue.Queue = queue.Queue()
        # ⚠️ timer 必须在 executor 开始 spin 之前创建（__init__ 阶段）才是安全的
        self._timer = node.create_timer(1.0 / hz, self._drain)
        self.dropped = 0

    def submit(self, fn, *args, **kwargs) -> concurrent.futures.Future:
        fut: concurrent.futures.Future = concurrent.futures.Future()
        self._q.put((fn, args, kwargs, fut))
        return fut

    def _drain(self) -> None:
        for _ in range(100):                       # 每 tick 最多处理 100 个，避免饿死 executor
            try:
                fn, args, kwargs, fut = self._q.get_nowait()
            except queue.Empty:
                return
            if fut.set_running_or_notify_cancel() is False:
                continue
            try:
                fut.set_result(fn(*args, **kwargs))
            except Exception as exc:               # 不让异常冒到 executor
                fut.set_exception(exc)


class ControlManager:
    """底盘 / 机械臂 / 夹爪 / 导航 / 急停 的统一入口。"""

    # 速度指令续期超时（秒）→ 超时自动归零（"死亡开关"）。
    # ⚠️ 2026-10-02 实测：300 ms 的余量太小 ——
    #   端到端固有延迟 = 前端续期 100ms + 后端发布周期 100ms + HTTP 往返（实测最差 ~300ms）
    #   实测"按住→车真的动"已达 **294 ms**，等于卡在阈值上；
    #   一旦某个续期迟到 >300 ms，看门狗就把指令清零，车就会"一动一停"、
    #   表现成"按住好几秒才有反应"（实测：续期间隔 150 ms 时只有 4/7 采样有速度）。
    # 800 ms 仍足以保证"断网/关页面就停"（0.3 m/s × 0.8 s = 24 cm 滑行），
    # 但把抗抖动余量从 1.5 倍提到 4 倍。需要更灵敏可调小。
    CMD_TIMEOUT = 0.8
    NAV_TIMEOUT = 120.0

    def __init__(self, node, store, config_path: str = DEFAULT_HARVEST_CFG,
                 webui_cfg: dict | None = None):
        self.node = node
        self.store = store
        self.dispatcher = RosDispatcher(node)
        self.cfg = self._load_config(config_path)
        wcfg = webui_cfg or {}

        # ── 底盘限速与看门狗 ──
        self.max_vx = float(wcfg.get('max_vx', 0.3))
        self.max_vy = float(wcfg.get('max_vy', 0.3))
        self.max_vth = float(wcfg.get('max_vth', 0.5))
        self.cmd_timeout = max(0.1, float(wcfg.get('cmd_timeout', self.CMD_TIMEOUT)))
        self._cmd = (0.0, 0.0, 0.0)
        self._cmd_ts = 0.0
        self._cmd_active = False
        # 最近一次速度指令的状态原因：renew(收到了续期) / timeout(看门狗清零) / estop
        # ⚠️ 必须从这里（/api/control）能读到 —— 以前只写进了 SSE 顶层，
        #   导致前端拿不到、排障时也找错地方（2026-10-02 修）。
        self._manual_reason = ''
        self._estop = False
        self._grasping = False                 # 单颗抓取序列进行中（防重入）
        self._last_grasp: dict = {}
        self._last_error = ''
        self._cmd_pub = node.create_publisher(Twist, '/cmd_vel', 1)
        self._cmd_timer = node.create_timer(0.1, self._cmd_tick)     # 10Hz 统一发布
        # 采摘任务命令（JSON，见 task_command）
        self._task_pub = node.create_publisher(String, '/grape_harvest/command', 10)

        # ── 机械臂工作空间（mm）与安全点 ──
        arm = (self.cfg.get('arm') or {})
        self.arm_cfg = arm                      # 抓取序列要用的参数（工具偏移/过渡点/安全点）
        # ── 抓取点补偿（可在网页上实时调 + 手动保存回配置文件）──
        # 为什么用独立 writer：ControlManager 只管“内存值立即生效”，
        # 文件回写（保注释、原子替换、双路径）交给 compensation.ConfigWriter。
        self.comp = ConfigWriter()
        self._comp_disk = self.comp.read()      # 磁盘上的值（用于“有未保存改动”判断/撤销）
        self.ws = {
            'x_min': float(arm.get('workspace_x_min', 30)),
            'x_max': float(arm.get('workspace_x_max', 335)),
            'y_min': float(arm.get('workspace_y_min', -190)),
            'y_max': float(arm.get('workspace_y_max', 190)),
            'z_min': float(arm.get('workspace_z_min', 20)),
            'z_max': float(arm.get('workspace_z_max', 220)),
        }

        # ── 服务客户端（创建在 __init__，此时还没 spin → 安全）──
        self.cli_goto = node.create_client(Move, 'goto_position')
        self.cli_rel = node.create_client(RelativePos, 'relative_position')
        self.cli_home = node.create_client(SetBool, 'home')
        self.cli_unlock = node.create_client(SetBool, 'unlock')
        self.cli_zero = node.create_client(SetBool, 'set_zero')
        self.cli_grip = node.create_client(SetBool, 'gripper/grip')

        # ── 导航 ──
        self.nav_client = None
        self._goal_handle = None
        if _NAV_OK:
            from rclpy.action import ActionClient
            self.nav_client = ActionClient(node, NavigateToPose, '/navigate_to_pose')
        self._init_pose_pub = node.create_publisher(
            PoseWithCovarianceStamped, '/initialpose', 1)

        # ── 航点（来自 harvest_config.yaml）──
        self.waypoints = self._parse_waypoints(self.cfg.get('waypoints') or [])
        self.nav_home_pose = {'x': float(wcfg.get('nav_home_x', 0.0)),
                              'y': float(wcfg.get('nav_home_y', 0.0)),
                              'yaw': 0.0}

    # ══════════ 配置 ══════════

    @staticmethod
    def _load_config(path: str) -> dict:
        for p in (path, DEFAULT_HARVEST_CFG,
                  '/home/ubuntu/ros2fox/install/fox_grape_harvest/share/fox_grape_harvest/config/harvest_config.yaml'):
            if p and os.path.exists(p):
                try:
                    with open(p) as f:
                        return yaml.safe_load(f) or {}
                except Exception:
                    continue
        return {}

    @staticmethod
    def _parse_waypoints(raw) -> list:
        out = []
        for i, wp in enumerate(raw):
            pos = (wp or {}).get('position') or {}
            ori = (wp or {}).get('orientation') or {}
            z = float(ori.get('z', 0.0))
            w = float(ori.get('w', 1.0))
            yaw = 2.0 * math.atan2(z, w)          # 小角度近似也够用
            out.append({
                'id': i,
                'x': float(pos.get('x', 0.0)),
                'y': float(pos.get('y', 0.0)),
                'yaw': yaw,
                'desc': (wp or {}).get('description') or f'航点 {i + 1}',
            })
        return out

    @staticmethod
    def _flatten(fut: concurrent.futures.Future) -> concurrent.futures.Future:
        """把"Future 里套 Future"拍平成一层，供 async 侧 await 一次即可。

        背景：dispatcher 的 job 是个在 executor 线程跑的普通函数；当它要发服务/action
        时只能返回一个等待响应的 Future（不能阻塞）。拍平后调用方无需关心这个细节。
        """
        out: concurrent.futures.Future = concurrent.futures.Future()

        def _done(f):
            if out.done():
                return
            try:
                r = f.result()
            except Exception as exc:
                out.set_exception(exc)
                return
            if isinstance(r, concurrent.futures.Future):
                r.add_done_callback(_done)          # 继续等内层
            else:
                out.set_result(r)

        fut.add_done_callback(_done)
        return out

    # ══════════ 底盘：指令 + 看门狗 ══════════

    def set_cmd_vel(self, vx: float, vy: float, vth: float) -> dict:
        """记录期望速度（不直接发；由 _cmd_tick 统一发布）。"""
        if self._estop:
            return {'ok': False, 'error': '急停锁定中，请先解除急停'}

        def clamp(v, lim):
            return max(-lim, min(lim, float(v)))

        self._cmd = (clamp(vx, self.max_vx), clamp(vy, self.max_vy),
                     clamp(vth, self.max_vth))
        self._cmd_ts = time.time()
        self._cmd_active = True
        self._manual_reason = 'renew'
        return {'ok': True, 'cmd': self._cmd}

    def _publish_cmd(self, vx, vy, vth) -> None:
        msg = Twist()
        msg.linear.x = float(vx)
        msg.linear.y = float(vy)
        msg.angular.z = float(vth)
        self._cmd_pub.publish(msg)

    def _cmd_tick(self) -> None:
        """10Hz：统一发布速度指令 + 看门狗自动归零（executor 线程）。"""
        now = time.time()
        if self._estop:
            self._publish_cmd(0.0, 0.0, 0.0)
            self._manual_reason = 'estop'
            return
        if not self._cmd_active:
            return
        if now - self._cmd_ts > self.cmd_timeout:
            self._cmd_active = False
            self._cmd = (0.0, 0.0, 0.0)
            self._manual_reason = 'timeout'
            self._publish_cmd(0.0, 0.0, 0.0)       # 松手/断网 → 立即停
            self.store.update(manual={'vx': 0.0, 'vy': 0.0, 'vth': 0.0,
                                      'active': False, 'reason': 'timeout'})
            return
        self._publish_cmd(*self._cmd)
        self.store.update(manual={'vx': self._cmd[0], 'vy': self._cmd[1],
                                  'vth': self._cmd[2], 'active': True})

    # ══════════ 急停 ══════════

    def estop(self, reason: str = 'manual') -> dict:
        self._estop = True
        self._cmd_active = False
        self._cmd = (0.0, 0.0, 0.0)
        self._publish_cmd(0.0, 0.0, 0.0)           # 立刻发一次零（不等 timer）
        cancelled = False
        if self._goal_handle is not None:
            try:
                self._goal_handle.cancel_goal_async()
                cancelled = True
            except Exception as exc:
                self._last_error = f'取消导航失败: {exc}'
        self.store.update(estop={'latched': True, 'reason': reason,
                                 'ts': time.time()})
        self.node.get_logger().warn(
            f'[control] 🚨 急停已触发 (reason={reason}, 导航已取消={cancelled})')
        return {'ok': True, 'estop': True, 'nav_cancelled': cancelled}

    def estop_release(self) -> dict:
        self._estop = False
        self.store.update(estop={'latched': False, 'ts': time.time()})
        self.node.get_logger().info('[control] 急停已解除')
        return {'ok': True, 'estop': False}

    # ══════════ 机械臂 ══════════

    def in_workspace(self, x: float, y: float, z: float) -> tuple[bool, str]:
        bad = []
        if not (self.ws['x_min'] <= x <= self.ws['x_max']):
            bad.append('X')
        if not (self.ws['y_min'] <= y <= self.ws['y_max']):
            bad.append('Y')
        if not (self.ws['z_min'] <= z <= self.ws['z_max']):
            bad.append('Z')
        if bad:
            return False, ('超出工作空间: ' + ','.join(bad) +
                           f" (X[{self.ws['x_min']:.0f},{self.ws['x_max']:.0f}]"
                           f" Y[{self.ws['y_min']:.0f},{self.ws['y_max']:.0f}]"
                           f" Z[{self.ws['z_min']:.0f},{self.ws['z_max']:.0f}])")
        return True, ''

    def arm_goto(self, x: float, y: float, z: float, roll: float = -1.0):
        """绝对移动（mm）。越界直接拒绝，不透传给驱动。"""
        ok, why = self.in_workspace(x, y, z)
        if not ok:
            f = concurrent.futures.Future()
            f.set_result({'ok': False, 'error': why})
            return f
        return self.arm_goto_unchecked(x, y, z, roll)

    def arm_goto_unchecked(self, x: float, y: float, z: float, roll: float = -1.0):
        """**不做工作空间检查**的绝对移动，只给“配置里的固定安全点”用。

        为什么不能用工作空间盒去管它们：那个盒描述的是“葡萄能不能被夹到”，
        而不是“机械臂合法位置集合”。现场配置的 home_x=0 就在盒外（x_min=30），
        一旦拦它，抓取最后“回安全点”那步会永远失败（实测踩过：
        `回安全点 ❌ 超出工作空间: X`）。参考脚本 grape_grasp_test.py 也是无条件执行。
        视觉算出来的抓取点仍然走带检查的 arm_goto。
        """
        def _job():
            if not self.cli_goto.service_is_ready():
                return {'ok': False, 'error': 'goto_position 服务不可用（机械臂节点未启动）'}
            req = Move.Request()
            req.pose.position.x = float(x)
            req.pose.position.y = float(y)
            req.pose.position.z = float(z)
            req.pose.roll = float(roll)
            fut = self.cli_goto.call_async(req)
            out = concurrent.futures.Future()

            def _done(f):
                if out.done():
                    return
                try:
                    r = f.result()
                    out.set_result({'ok': bool(r.success), 'message': r.message})
                except Exception as exc:
                    out.set_exception(exc)

            fut.add_done_callback(_done)
            return out                              # dispatcher 会把 Future 解出

        return self._flatten(self.dispatcher.submit(_job))

    def arm_relative(self, dx: float, dy: float, dz: float):
        cur = (self.store.snapshot().get('arm') or None)
        if cur is not None:
            ok, why = self.in_workspace(cur['x'] + dx, cur['y'] + dy, cur['z'] + dz)
            if not ok:
                f = concurrent.futures.Future()
                f.set_result({'ok': False, 'error': '相对移动会' + why})
                return f

        def _job():
            if not self.cli_rel.service_is_ready():
                return {'ok': False, 'error': 'relative_position 服务不可用'}
            req = RelativePos.Request()
            req.dx, req.dy, req.dz = float(dx), float(dy), float(dz)
            fut = self.cli_rel.call_async(req)
            out = concurrent.futures.Future()

            def _done(f):
                if out.done():
                    return
                try:
                    r = f.result()
                    out.set_result({'ok': bool(r.success), 'message': r.message})
                except Exception as exc:
                    out.set_exception(exc)

            fut.add_done_callback(_done)
            return out

        return self._flatten(self.dispatcher.submit(_job))

    def arm_home(self):
        return self._simple_service(self.cli_home, 'home')

    def arm_unlock(self, confirm: bool):
        """解锁电机（可用手扳动）—— 危险，必须显式确认。"""
        if not confirm:
            f = concurrent.futures.Future()
            f.set_result({'ok': False, 'error': '危险操作需要二次确认 (confirm=true)'})
            return f
        return self._simple_service(self.cli_unlock, 'unlock')

    def arm_set_zero(self, confirm: bool):
        """把当前位姿设为零点 —— 危险，必须显式确认。"""
        if not confirm:
            f = concurrent.futures.Future()
            f.set_result({'ok': False, 'error': '危险操作需要二次确认 (confirm=true)'})
            return f
        return self._simple_service(self.cli_zero, 'set_zero')

    def _simple_service(self, client, name: str):
        def _job():
            if not client.service_is_ready():
                return {'ok': False, 'error': f'{name} 服务不可用'}
            req = SetBool.Request()
            req.data = True
            fut = client.call_async(req)
            out = concurrent.futures.Future()

            def _done(f):
                if out.done():
                    return
                try:
                    r = f.result()
                    out.set_result({'ok': bool(r.success), 'message': r.message})
                except Exception as exc:
                    out.set_exception(exc)

            fut.add_done_callback(_done)
            return out

        return self._flatten(self.dispatcher.submit(_job))

    # ══════════ 夹爪 ══════════

    def gripper(self, close: bool):
        def _job():
            if not self.cli_grip.service_is_ready():
                return {'ok': False, 'error': 'gripper/grip 服务不可用（夹爪节点未启动）'}
            req = SetBool.Request()
            req.data = bool(close)
            fut = self.cli_grip.call_async(req)
            out = concurrent.futures.Future()

            def _done(f):
                if out.done():
                    return
                try:
                    r = f.result()
                    out.set_result({'ok': bool(r.success), 'message': r.message,
                                    'close': bool(close)})
                except Exception as exc:
                    out.set_exception(exc)

            fut.add_done_callback(_done)
            return out

        return self._flatten(self.dispatcher.submit(_job))

    # ══════════ 导航 ══════════

    def nav_goal(self, x: float, y: float, yaw: float = 0.0):
        def _job():
            if self.nav_client is None:
                return {'ok': False, 'error': '本环境没有 nav2_msgs'}
            if not self.nav_client.server_is_ready():
                return {'ok': False, 'error': '导航未就绪（Nav2 未启动或未激活）'}
            goal = NavigateToPose.Goal()
            goal.pose.header.frame_id = 'map'
            goal.pose.header.stamp = self.node.get_clock().now().to_msg()
            goal.pose.pose.position.x = float(x)
            goal.pose.pose.position.y = float(y)
            goal.pose.pose.orientation.z = math.sin(float(yaw) / 2.0)
            goal.pose.pose.orientation.w = math.cos(float(yaw) / 2.0)
            out = concurrent.futures.Future()
            send_fut = self.nav_client.send_goal_async(
                goal, feedback_callback=self._on_nav_feedback)
            send_fut.add_done_callback(lambda f: self._on_goal_response(f, out, x, y, yaw))
            return out

        return self._flatten(self.dispatcher.submit(_job))

    def _on_goal_response(self, fut, out: concurrent.futures.Future,
                          x: float, y: float, yaw: float) -> None:
        if out.done():
            return
        try:
            handle = fut.result()
        except Exception as exc:
            out.set_result({'ok': False, 'error': f'发送目标失败: {exc}'})
            return
        if handle is None or not handle.accepted:
            out.set_result({'ok': False, 'error': '目标被拒绝（可能不可达/被禁行区挡住）'})
            return
        self._goal_handle = handle
        self.node.get_logger().info(f'[control] 导航目标已接受: ({x:.2f}, {y:.2f})')
        out.set_result({'ok': True, 'accepted': True, 'target': [x, y, yaw]})
        result_fut = handle.get_result_async()
        result_fut.add_done_callback(self._on_nav_result)

    def _on_nav_result(self, fut) -> None:
        self._goal_handle = None
        try:
            res = fut.result()
            status = getattr(res, 'status', None)
        except Exception:
            status = None
        self.node.get_logger().info(f'[control] 导航结束 (status={status})')
        self.store.update(nav={'active': False, 'status': status})

    def _on_nav_feedback(self, msg) -> None:
        try:
            fb = msg.feedback
            self.store.update(nav={
                'active': True,
                'distance_remaining': round(float(fb.distance_remaining), 2),
                'navigation_time_s': round(
                    float(fb.navigation_time.sec) + float(fb.navigation_time.nanosec) * 1e-9, 1),
                'recoveries': int(fb.number_of_recoveries),
            })
        except Exception:
            pass

    def nav_cancel(self):
        def _job():
            if self._goal_handle is None:
                return {'ok': True, 'cancelled': False, 'note': '当前没有导航目标'}
            try:
                self._goal_handle.cancel_goal_async()
            except Exception as exc:
                return {'ok': False, 'error': str(exc)}
            self.store.update(nav={'active': False, 'cancelled': True})
            return {'ok': True, 'cancelled': True}

        return self._flatten(self.dispatcher.submit(_job))

    def nav_home(self):
        """导航回原点。

        ⚠️ 注意别把"回原点坐标"这个属性也叫 self.nav_home：实例属性会盖住同名方法，
        调用 control.nav_home() 会变成 "'dict' object is not callable"（已踩）。
        属性叫 self.nav_home_pose。
        """
        return self.nav_goal(self.nav_home_pose['x'], self.nav_home_pose['y'],
                             self.nav_home_pose['yaw'])

    # ══════════ 初始位姿（lidar_loc / AMCL 都需要）══════════

    def set_initial_pose(self, x: float, y: float, yaw: float = 0.0):
        def _job():
            msg = PoseWithCovarianceStamped()
            msg.header.frame_id = 'map'
            msg.header.stamp = self.node.get_clock().now().to_msg()
            msg.pose.pose.position.x = float(x)
            msg.pose.pose.position.y = float(y)
            msg.pose.pose.orientation.z = math.sin(float(yaw) / 2.0)
            msg.pose.pose.orientation.w = math.cos(float(yaw) / 2.0)
            msg.pose.covariance[0] = 0.25
            msg.pose.covariance[7] = 0.25
            msg.pose.covariance[35] = 0.07
            self._init_pose_pub.publish(msg)
            return {'ok': True, 'pose': [x, y, yaw]}

        return self._flatten(self.dispatcher.submit(_job))

    # ══════════ 采摘任务（发给 harvest_node 的命令话题）══════════

    def task_command(self, cmd: str, **kw):
        """发一条采摘任务命令（JSON）到 /grape_harvest/command。

        为什么用话题而不是服务/action：harvest_node 跑流程时是在回调里同步跑的，
        服务响应保证不了准时；话题 + 协作式取消标志最简单可靠。
        状态走 /grape_harvest/status → state.py 解析后进 state.task。
        """
        payload = {'cmd': str(cmd)}
        for k, v in kw.items():
            if v is not None:
                payload[k] = v

        def _job():
            msg = String()
            msg.data = json.dumps(payload, ensure_ascii=False)
            self._task_pub.publish(msg)
            return {'ok': True, 'published': payload,
                    'subscribers': int(self._task_pub.get_subscription_count())}

        return self._flatten(self.dispatcher.submit(_job))

    # ══════════ 抓取点补偿（页面实时调 + 手动保存到配置）══════════

    def compensation(self) -> dict:
        """当前补偿值（内存）、磁盘值、是否有未保存改动、限幅与文件路径。"""
        cur = {k: float(self.arm_cfg.get(k, 0.0)) for k in COMP_KEYS}
        disk = {k: float(self._comp_disk.get(k, cur[k])) for k in COMP_KEYS}
        dirty = {k: (abs(cur[k] - disk[k]) > 1e-9) for k in COMP_KEYS}
        return {
            'keys': list(COMP_KEYS),
            'value': cur,                    # 当前生效值
            'disk': disk,                    # 上次保存到文件的值
            'dirty': any(dirty.values()),
            'dirty_keys': [k for k, v in dirty.items() if v],
            'limit_mm': COMP_LIMIT,
            'paths': list(self.comp.paths),
            'last_save': self.comp.last_save,
            'note': '抓取点 = 葡萄坐标 + 按朝向旋转过的该偏移（与 grape_grasp_test.py 同款）',
        }

    def set_compensation(self, values: dict, save: bool = False) -> dict:
        """修改补偿值。save=False → 只改内存（下一次抓取立即生效）；
        save=True  → 同时回写配置文件（保留注释、双路径、自动备份）。

        允许传单个轴或 {dx,dy,dz} 增量（delta_* 形式），便于前端步进按钮。
        """
        patch = {}
        for k in COMP_KEYS:
            if k in values and values[k] is not None:
                patch[k] = values[k]
        # 增量形式：dx/dy/dz 或 delta_x/...
        for short, full in (('dx', 'tool_offset_x'), ('dy', 'tool_offset_y'),
                            ('dz', 'tool_offset_z')):
            for name in (short, 'delta_' + short[-1]):
                if values.get(name) is not None:
                    base = float(patch.get(full, self.arm_cfg.get(full, 0.0)))
                    patch[full] = base + float(values[name])

        if not patch:
            return {'ok': False, 'error': f'没有有效字段（允许 {list(COMP_KEYS)} 或 dx/dy/dz）'}

        # 限幅
        merged = {k: float(patch.get(k, self.arm_cfg.get(k, 0.0))) for k in COMP_KEYS}
        if any(abs(v) > COMP_LIMIT for v in merged.values()):
            bad = {k: v for k, v in merged.items() if abs(v) > COMP_LIMIT}
            return {'ok': False, 'error': f'超出限幅 ±{COMP_LIMIT:g} mm: {bad}'}

        # 立即生效：改的就是 grasp_sequence()/_tool_offset_robot() 读的那份 dict
        for k, v in patch.items():
            self.arm_cfg[k] = float(v)
        self.node.get_logger().info(
            f"[comp] 抓取点补偿更新: "
            + ', '.join(f'{k}={self.arm_cfg[k]:.1f}' for k in COMP_KEYS)
            + ('（已保存到配置文件）' if save else '（仅内存，未保存）'))

        out = {'ok': True, 'saved': False, **self.compensation()}
        if save:
            res = self.save_compensation()
            out.update({'saved': bool(res.get('ok')), 'save_result': res})
            out['ok'] = bool(res.get('ok'))
            if not res.get('ok'):
                out['error'] = res.get('error') or '写入配置文件失败'
        return out

    def save_compensation(self) -> dict:
        """把当前内存里的补偿值回写到配置文件（保留注释 + 双路径 + 自动备份）。

        写完后如果 harvest 节点在听命令话题，就顺手发一条 reload —— 这样“一键采摘”
        的完整流程也立即用上新补偿，不需要重启节点。
        """
        values = {k: float(self.arm_cfg.get(k, 0.0)) for k in COMP_KEYS}
        res = self.comp.save(values)
        if res.get('ok'):
            self._comp_disk = self.comp.read()   # 以磁盘为准刷新快照
            self.node.get_logger().info(
                f"[comp] 已保存到: {', '.join(res.get('paths', []))}")
            res['harvest_reloaded'] = False
            try:
                if int(self._task_pub.get_subscription_count()) > 0:
                    self.task_command('reload')            # 异步发，不等结果
                    res['harvest_reloaded'] = True
            except Exception as exc:
                self.node.get_logger().warn(f'[comp] 通知 harvest 重读失败: {exc}')
        else:
            self.node.get_logger().error(f"[comp] 保存失败: {res}")
        return res

    def revert_compensation(self) -> dict:
        """丢弃未保存改动，回到磁盘上的值。"""
        disk = self.comp.read()
        if not disk:
            return {'ok': False, 'error': '读不到配置文件里的补偿值'}
        for k in COMP_KEYS:
            self.arm_cfg[k] = float(disk.get(k, self.arm_cfg.get(k, 0.0)))
        self._comp_disk = disk
        self.node.get_logger().info('[comp] 已撤销未保存改动，回到配置文件里的值')
        return {'ok': True, **self.compensation()}

    # ══════════ 单颗抓取（与 scripts/grape_grasp_test.py 同款动作序列）══════════

    def _tool_offset_robot(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        """把夹爪【局部坐标系】偏移旋转到机器人坐标系（与 grape_grasp_test.py 一致）。

        局部系定义（机械臂基座为原点）：
          tool_offset_x: 沿机械臂指向目标的径向方向
          tool_offset_y: 侧向（垂直径向，向左为正）
          tool_offset_z: 垂直方向（不受朝向影响）
        机械臂朝向 θ = atan2(y, x)。这样葡萄在左/右/前不同位姿时偏移都能正确补偿，
        避免常数偏移在 Y 上随朝向变化导致“往前调好往后又偏”。
        """
        ox_l = float(self.arm_cfg.get('tool_offset_x', 0.0))
        oy_l = float(self.arm_cfg.get('tool_offset_y', 0.0))
        oz_l = float(self.arm_cfg.get('tool_offset_z', 0.0))
        theta = math.atan2(float(y), float(x))
        c, s = math.cos(theta), math.sin(theta)
        return (ox_l * c - oy_l * s, ox_l * s + oy_l * c, oz_l)

    def _seq_params(self) -> dict:
        """抓取序列参数（全部来自 harvest_config.yaml，与脚本同一份配置）。"""
        ws = self.ws
        mid = ((ws['x_min'] + ws['x_max']) / 2.0,
               (ws['y_min'] + ws['y_max']) / 2.0,
               (ws['z_min'] + ws['z_max']) / 2.0)
        return {
            'transition': (float(self.arm_cfg.get('transition_x', mid[0])),
                           float(self.arm_cfg.get('transition_y', mid[1])),
                           float(self.arm_cfg.get('transition_z', mid[2]))),
            'home': (float(self.arm_cfg.get('home_x', 0.0)),
                     float(self.arm_cfg.get('home_y', -120.0)),
                     float(self.arm_cfg.get('home_z', 60.0))),
            'grip_delay': float(self.arm_cfg.get('grip_delay', 1.0)),
        }

    def grasp_sequence(self, x: float, y: float, z: float):
        """单颗抓取：**与 scripts/grape_grasp_test.py 完全同款的 5 步动作**。

            1. 先去过渡点（工作空间范围中点）
            2. 到抓取点（葡萄坐标 + 按朝向旋转后的工具偏移）
            3. 夹爪夹紧
            4. 回安全点（home）
            5. 在安全点松开（把葡萄放下）

        与 harvest_node 的“抓完放车上篮子”不同 —— 这里按现场习惯的脚本流程走。

        线程模型：序列由一个 worker 线程逐步调度，每一步都只把“一次服务调用”丢给
        RosDispatcher（executor 线程执行），worker 只等 Future —— 绝不跨线程碰 rclpy；
        这样也不会长时间占住 dispatcher（它还要跑速度看门狗）。
        """
        out: concurrent.futures.Future = concurrent.futures.Future()

        ok, why = self.in_workspace(x, y, z)
        if not ok:
            out.set_result({'ok': False, 'error': why, 'target': [x, y, z]})
            return out
        if self._estop:
            out.set_result({'ok': False, 'error': '急停锁定中，请先解除急停'})
            return out
        if self._grasping:
            out.set_result({'ok': False, 'error': '上一次抓取还没结束'})
            return out
        missing = [n for n, c in (('goto_position', self.cli_goto),
                                  ('gripper/grip', self.cli_grip))
                   if not c.service_is_ready()]
        if missing:
            out.set_result({'ok': False,
                            'error': f'服务不可用: {missing}（先在“模块启停”里启动 arm 与 gripper）'})
            return out

        self._grasping = True
        self._last_grasp = {'target': [x, y, z], 'started': time.time(),
                            'steps': [], 'running': True}

        def _step(name: str, fut, timeout: float) -> dict:
            """等一步完成（worker 线程里等 Future，不碰 rclpy）。"""
            rec = {'name': name, 'ok': False, 'detail': ''}
            try:
                res = fut.result(timeout=timeout)
                rec['ok'] = bool((res or {}).get('ok'))
                rec['detail'] = str((res or {}).get('message') or (res or {}).get('error') or '')
            except Exception as exc:
                rec['detail'] = f'{type(exc).__name__}: {exc}'
            self._last_grasp['steps'] = self._last_grasp['steps'] + [rec]
            self.node.get_logger().info(
                f"[grasp] {name}: {'✅' if rec['ok'] else '❌'} {rec['detail']}")
            return rec

        def _run() -> None:
            p = self._seq_params()
            tx, ty, tz = p['transition']
            hx, hy, hz = p['home']
            ox, oy, oz = self._tool_offset_robot(x, y, z)
            gx, gy, gz = x + ox, y + oy, z + oz
            self.node.get_logger().info(
                f'🍇 [grasp] 葡萄({x:.0f},{y:.0f},{z:.0f}) → 抓取点({gx:.0f},{gy:.0f},{gz:.0f}) '
                f'(工具偏移 {ox:+.0f},{oy:+.0f},{oz:+.0f})')
            steps = []
            try:
                # 1. 过渡点（固定安全点，不做工作空间检查）
                steps.append(_step('到过渡点', self.arm_goto_unchecked(tx, ty, tz), 35.0))
                time.sleep(0.5)
                # 2. 抓取点（视觉算出 → 保留越界拦截）
                if steps[-1]['ok']:
                    steps.append(_step('到抓取点', self.arm_goto(gx, gy, gz), 35.0))
                    time.sleep(0.5)
                # 3. 夹紧
                if steps and steps[-1]['ok']:
                    steps.append(_step('夹紧', self.gripper(True), 20.0))
                    time.sleep(p['grip_delay'])
                # 4/5. 回安全点 + 松开（脚本里即使前面失败也会回安全点，保持一致）
                steps.append(_step('回安全点', self.arm_goto_unchecked(hx, hy, hz), 35.0))
                steps.append(_step('松开', self.gripper(False), 20.0))

                ok_first3 = all(s['ok'] for s in steps[:3]) if len(steps) >= 3 else False
                out.set_result({
                    'ok': ok_first3,
                    'target': [x, y, z],
                    'grasp_point': [gx, gy, gz],
                    'transition': [tx, ty, tz],
                    'home': [hx, hy, hz],
                    'steps': steps,
                    'message': ('抓取完成（已回安全点并松开）' if ok_first3
                                else '抓取未成功，已回安全点'),
                })
            except Exception as exc:
                out.set_exception(exc)
            finally:
                self._grasping = False
                self._last_grasp['running'] = False
                self._last_grasp['finished'] = time.time()

        threading.Thread(target=_run, name='grasp-seq', daemon=True).start()
        return out

    # ══════════ 状态快照（给前端渲染）══════════

    def status(self) -> dict:
        return {
            'estop': self._estop,
            'manual': {'vx': self._cmd[0], 'vy': self._cmd[1], 'vth': self._cmd[2],
                       'active': self._cmd_active, 'reason': self._manual_reason},
            'limits': {'max_vx': self.max_vx, 'max_vy': self.max_vy,
                       'max_vth': self.max_vth, 'cmd_timeout': self.cmd_timeout},
            'workspace': self.ws,
            'waypoints': self.waypoints,
            'nav_home': self.nav_home_pose,
            'nav_active': self._goal_handle is not None,
            'last_error': self._last_error,
            'grasping': self._grasping,
            'last_grasp': self._last_grasp,
            'compensation': {'value': {k: float(self.arm_cfg.get(k, 0.0)) for k in COMP_KEYS},
                             'dirty': self.compensation()['dirty']},
            'task_listening': int(self._task_pub.get_subscription_count()) > 0,
            'services': {
                'goto_position': bool(self.cli_goto.service_is_ready()),
                'relative_position': bool(self.cli_rel.service_is_ready()),
                'home': bool(self.cli_home.service_is_ready()),
                'unlock': bool(self.cli_unlock.service_is_ready()),
                'set_zero': bool(self.cli_zero.service_is_ready()),
                'gripper/grip': bool(self.cli_grip.service_is_ready()),
                'navigate_to_pose': bool(self.nav_client and self.nav_client.server_is_ready()),
            },
        }
