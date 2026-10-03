"""状态采集层：把 ROS2 话题 / TF 汇聚成一份"带锁的快照"，供 Web 层读取。

设计要点（详见 docs/WebUI_技术文档.md §5.1）
------------------------------------------------
* ROS 回调线程（高频，可能 50Hz）**只写** StateStore；
* Web 线程（HTTP / SSE / MJPEG）**只读** 快照，从不直接调用 ROS 接口；
* 两边用一把可重入锁解耦，避免"跨线程调用 asyncio"这类经典翻车点；
* 订阅图像类话题只做"到达心跳"（不转 cv_bridge），保证不看视频时几乎零开销。

单位约定（本项目实测，务必遵守）
------------------------------------------------
* 深度话题 16UC1 单位是 **厘米(cm)** → 米要 /100（不是 /1000）；
* 机械臂 /arm_controller/position_info 单位是 **毫米(mm)**；
* 底盘 /odom 线速度 m/s，角速度 rad/s。
"""
from __future__ import annotations

import json
import math
import threading
import time
from collections import deque

from rclpy.qos import (
    QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data,
)

from std_msgs.msg import Int32, String
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry, OccupancyGrid, Path
from sensor_msgs.msg import CameraInfo, LaserScan
from rcl_interfaces.msg import Log

from arm_controller.msg import Control
from rei_robot_base.msg import CarData

try:
    from tf2_ros import Buffer, TransformListener
    from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
    _TF_OK = True
except Exception:                                    # pragma: no cover
    Buffer = None
    _TF_OK = False

    class LookupException(Exception):
        pass

    class ConnectivityException(Exception):
        pass

    class ExtrapolationException(Exception):
        pass


# ────────────────────────── 工具函数 ──────────────────────────

def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    """四元数 → yaw(rad)。与 chassis_interface.py 使用同一公式，保证一致。"""
    siny = 2.0 * (w * z + x * y)
    cosy = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny, cosy)


def deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def r3(v: float) -> float:
    """保留 3 位小数，减小 SSE 负载。"""
    return round(float(v), 3)


# ────────────────────────── 健康度 ──────────────────────────

class TopicHealth:
    """单个话题的在线状态与频率估算。

    ⚠️ 每个话题的"多久没消息算掉线"必须区别对待（实测踩过）：
      * 周期话题（/odom 50Hz、/scan 10Hz）→ 3s 足够；
      * **事件驱动话题**（/rosout 只有打日志时才发、/cmd_vel 只有导航/遥控时才发、
        /gripper/state 只有动作时才发）→ 用 3s 会疯狂误报"掉线"，必须放宽到 10~15s；
      * 静态/锁存话题（/map）→ 只发一次，用"是否收到过"判断，不按频率报警。
    """

    def __init__(self, topic: str, window: float = 3.0, static: bool = False,
                 hint_hz: float | None = None, timeout: float | None = None):
        self.topic = topic
        self.window = window
        self.static = static          # 静态/锁存话题（如 /map），低频率是正常的
        self.hint_hz = hint_hz        # 期望频率（仅用于界面提示）
        self.timeout = timeout        # 该话题的掉线判定阈值（None=用全局默认）
        self.last_ts = 0.0
        self.count = 0
        self._stamps = deque(maxlen=400)

    def tick(self) -> None:
        now = time.time()
        self.last_ts = now
        self.count += 1
        self._stamps.append(now)

    def snapshot(self, online_timeout: float = 3.0) -> dict:
        now = time.time()
        age = (now - self.last_ts) if self.last_ts else None
        limit = self.timeout if self.timeout is not None else online_timeout
        if self.static:
            limit = max(limit, 30.0)          # 静态地图：只要收到过就一直算在线
        hz = 0.0
        if self._stamps:
            recent = [t for t in self._stamps if now - t <= self.window]
            if len(recent) >= 2:
                span = max(recent[-1] - recent[0], 1e-6)
                hz = (len(recent) - 1) / span
        return {
            'topic': self.topic,
            'online': bool(age is not None and age <= limit),
            'hz': round(hz, 1),
            'age': None if age is None else round(age, 2),
            'count': self.count,
            'static': self.static,
            'hint_hz': self.hint_hz,
            'timeout': limit,
        }


# ────────────────────────── 快照仓库 ──────────────────────────

def default_state(robot_name: str = 'fox') -> dict:
    return {
        'ts': 0.0,
        'robot': {'name': robot_name, 'online': False},
        'pose': None,          # {x,y,yaw,frame_yaw_deg,src:'tf'|'lidar_loc'}
        'twist': {'vx': 0.0, 'vy': 0.0, 'vth': 0.0},     # /odom 实测
        'cmd_vel': {'vx': 0.0, 'vy': 0.0, 'vth': 0.0, 'age': None},
        'arm': None,           # {x,y,z,roll,pitch,yaw}(mm/deg)
        'gripper': None,       # {pulse, ratio, closed}
        'battery': None,       # {voltage, charging}
        'chassis': None,       # {motor_speed, crash, cliff, smoke, ultrasound}
        'scan': None,          # {frame, points:[[x,y],...], n} 已转换到 map 系
        'plan': None,          # {points:[[x,y],...], n}
        'task': None,          # /grape_harvest/status 解析后的 JSON（阶段/计数）
        'health': {},
    }


#: 模式 C 的紧凑视图要剔除的重字段（scan/plan 点集、健康表、模块表体积大，
#: 10Hz 推给浏览器会把 SSE 从 ~2KB 撑到十几 KB；需要时用 /api/to/<name>/… 或
#: /api/map_state 按需取）
_COMPACT_DROP = ('scan', 'plan', 'health', 'robots', 'modules')


def _compact(d: dict) -> dict:
    """去掉重字段，得到适合放进 SSE `robots` 的紧凑快照。"""
    return {k: v for k, v in (d or {}).items() if k not in _COMPACT_DROP}


class StateStore:
    """线程安全的状态快照仓库（ROS 线程写 / Web 线程读）。"""

    def __init__(self, robot_name: str = 'fox', log_buffer: int = 500,
                 health_window: float = 3.0, online_timeout: float = 3.0):
        self._lock = threading.RLock()
        self._data = default_state(robot_name)
        self._health: dict[str, TopicHealth] = {}
        self._logs: deque = deque(maxlen=log_buffer)
        self._log_seq = 0
        self.online_timeout = online_timeout
        self.gripper_pulse = {'open': 500, 'close': 2000}   # 项目实测: 2000=抓紧, 500=松开
        self._health_window = health_window
        # ── 模式 C（对称 HTTP 聚合）：邻居名单 + 邻居快照 ──
        # 由 peers.PeerAggregator 写入（HTTP 层，不经 rclpy），本机数据仍是"顶层扁平"结构。
        self._peers: dict[str, dict] = {}        # name -> {'url','online','last_ts','err'}
        self._peer_state: dict[str, dict] = {}   # name -> 邻居快照（已剔除重字段）

    # ── 健康 ──
    def register_topic(self, topic: str, static: bool = False,
                       hint_hz: float | None = None,
                       timeout: float | None = None) -> None:
        with self._lock:
            self._health.setdefault(
                topic, TopicHealth(topic, self._health_window, static, hint_hz, timeout))

    def tick(self, topic: str) -> None:
        with self._lock:
            h = self._health.get(topic)
            if h is None:
                meta = TOPIC_META.get(topic, {})
                h = TopicHealth(topic, self._health_window,
                                meta.get('static', False),
                                meta.get('hint_hz'),
                                meta.get('timeout'))
                self._health[topic] = h
            h.tick()

    def health(self) -> dict:
        with self._lock:
            return {t: h.snapshot(self.online_timeout) for t, h in self._health.items()}

    # ── 状态写入 ──
    def update(self, **patch) -> None:
        with self._lock:
            self._data.update(patch)
            self._data['ts'] = time.time()

    def snapshot(self) -> dict:
        with self._lock:
            snap = dict(self._data)
            snap['health'] = {t: h.snapshot(self.online_timeout)
                              for t, h in self._health.items()}
            # robot.online = 关键话题是否在线（底盘 odom 有数据即视为"在跑"）
            odom = snap['health'].get('/odom')
            snap['robot'] = dict(self._data['robot'])
            snap['robot']['online'] = bool(odom and odom['online'])
            # 模式 C：多机清单（紧凑版；本机数据仍在上面的顶层字段里，向后兼容）
            snap['robots'] = self._robots_index(snap['robot']['online'])
            return snap

    # ── 模式 C：邻居（对称 HTTP 聚合）──
    #
    # 这一组方法由 peers.PeerAggregator 的 **HTTP 采集线程** 调用（不是 rclpy 线程），
    # 与"ROS 实体只能在 executor 线程创建/销毁"（§5.3 铁律）无关，因此不会死锁。

    def set_peers(self, peers) -> None:
        """登记邻居名单（名字/URL）。由 `PeerAggregator.start()` 调用。"""
        me = self._data['robot']['name']
        with self._lock:
            for p in peers or []:
                name = str(p.get('name', '')).strip()
                if not name or name == me:
                    continue                      # 不把自己当邻居
                meta = self._peers.setdefault(name, {})
                meta.setdefault('online', False)
                meta.setdefault('last_ts', 0.0)
                meta.setdefault('err', '尚未连接')
                meta['url'] = str(p.get('url', '')).rstrip('/')

    def update_robot(self, name: str, snap: dict) -> None:
        """写入邻居快照（由 peers 采集线程调用）。"""
        with self._lock:
            self._peer_state[name] = _compact(snap or {})
            meta = self._peers.setdefault(name, {})
            meta.update({'online': True, 'last_ts': time.time(), 'err': ''})

    def mark_offline(self, name: str, err: str = '') -> None:
        """标记邻居掉线。**不清除旧快照** —— 页面还能显示"最后一次已知状态"。"""
        with self._lock:
            meta = self._peers.setdefault(name, {})
            meta.update({'online': False, 'err': err or '连接失败'})

    def peers_status(self) -> list:
        """邻居清单，供 `GET /api/robots`。

        ⚠️ 两个状态必须分开（实测踩过：混用会显示"本机离线、邻居在线"）：
          * `reachable` = **能不能连上该 Agent**（HTTP / 本机恒为 True）→ 决定能否切过去看；
          * `online`    = **该机的机器人数据在不在跑**（`/odom` 是否在线）→ 决定绿灯。
        """
        me = self._data['robot']['name']
        now = time.time()
        with self._lock:
            odom = self._health.get('/odom')
            me_online = bool(odom and odom.snapshot(self.online_timeout)['online'])
            out = [{'name': me, 'url': '', 'is_me': True,
                    'online': me_online, 'reachable': True, 'age': 0.0, 'err': ''}]
            for name, meta in self._peers.items():
                last = float(meta.get('last_ts') or 0.0)
                peer = self._peer_state.get(name) or {}
                reachable = bool(meta.get('online'))
                out.append({
                    'name': name,
                    'url': meta.get('url', ''),
                    'is_me': False,
                    # 不可达时恒为 False：连不上就不该说它"在线"（旧快照只当"最后已知状态"）
                    'online': reachable and bool((peer.get('robot') or {}).get('online')),
                    'reachable': reachable,
                    'age': None if not last else round(now - last, 2),
                    'err': meta.get('err', ''),
                })
        return out

    def _robots_index(self, me_online: bool) -> dict:
        """SSE 的 `robots` 映射 `{名字: 紧凑快照}`。

        ⚠️ 遍历的是 `self._peers`（登记过的全部邻居），**不是** `self._peer_state`（收到过
        快照的）。否则"从启动起就一直连不上"的邻居会连名字都不出现在下拉里，
        用户会以为配置没生效 —— 实测踩过。没收到过快照的只给状态字段，其余缺省。

        两个状态的语义见 `peers_status()` 的说明（reachable / online）。
        """
        me = self._data['robot']['name']
        out = {me: dict(_compact(self._data), online=me_online, reachable=True,
                        is_me=True, url='', age=0.0)}
        now = time.time()
        for name, meta in self._peers.items():
            entry = dict(self._peer_state.get(name) or {})
            reachable = bool(meta.get('online'))
            last = float(meta.get('last_ts') or 0.0)
            entry.update(reachable=reachable,
                         online=reachable and bool((entry.get('robot') or {}).get('online')),
                         is_me=False, url=meta.get('url', ''), err=meta.get('err', ''),
                         age=None if not last else round(now - last, 2))
            out[name] = entry
        return out

    # ── 日志 ──
    def push_log(self, level: int, name: str, msg: str) -> None:
        with self._lock:
            self._log_seq += 1
            self._logs.append({
                'id': self._log_seq,
                't': round(time.time(), 3),
                'level': int(level),
                'name': name,
                'msg': msg,
            })

    def logs_since(self, since_id: int = 0, limit: int = 200) -> list:
        with self._lock:
            out = [e for e in self._logs if e['id'] > since_id]
        return out[-limit:]

    def set_gripper_pulse_range(self, open_pulse: int, close_pulse: int) -> None:
        with self._lock:
            self.gripper_pulse = {'open': int(open_pulse), 'close': int(close_pulse)}

    def gripper_ratio(self, pulse: int) -> float:
        """脉宽 → 开度(0=全闭 1=全开)。项目实测: 2000=抓紧(闭), 500=松开(开)。"""
        o = self.gripper_pulse['open']
        c = self.gripper_pulse['close']
        if c == o:
            return 0.0
        r = (c - pulse) / float(c - o)
        return max(0.0, min(1.0, r))


# ────────────────────────── 采集器 ──────────────────────────

#: 话题元信息：期望频率 / 是否静态 / **掉线阈值(秒)**
#:
#: timeout 是实测踩出来的关键参数：事件驱动话题若沿用统一的 3s，会不停闪"掉线"
#:   - /rosout 只在有日志时才发（心跳型日志可能 5s 一条）→ 20s
#:   - /cmd_vel 只在导航/遥控时发 → 10s
#:   - /gripper/state 只在夹爪动作时发 → 15s
#:   - /plan 只在导航中发 → 20s
TOPIC_META = {
    '/odom':                         {'hint_hz': 50.0, 'timeout': 3.0},
    '/cmd_vel':                      {'hint_hz': None, 'timeout': 10.0},
    '/car_data':                     {'hint_hz': 50.0, 'timeout': 3.0},
    '/arm_controller/position_info': {'hint_hz': 10.0, 'timeout': 3.0},
    '/gripper/state':                {'hint_hz': None, 'timeout': 15.0},
    '/lidar_loc_pose':               {'hint_hz': 30.0, 'timeout': 5.0},
    '/rosout':                       {'hint_hz': None, 'timeout': 20.0},
    '/scan':                         {'hint_hz': 10.0, 'timeout': 3.0},
    '/camera/color/camera_info':     {'hint_hz': 30.0, 'timeout': 5.0},
    '/camera/color/image_raw':       {'hint_hz': 30.0, 'timeout': 5.0},
    '/camera/depth/image_raw':       {'hint_hz': 30.0, 'timeout': 5.0},
    '/plan':                         {'hint_hz': 1.0, 'timeout': 20.0},
    '/map':                          {'hint_hz': None, 'static': True},
    # 采摘任务状态（1Hz 心跳 + 变化立即发）→ 超时给宽一点，避免空闲时闪"掉线"
    '/grape_harvest/status':         {'hint_hz': 1.0, 'timeout': 15.0},
}

#: 只做"到达心跳"的话题（不转 cv_bridge，开销极小）：(话题, 消息类型, QoS 选型)
#: ⚠️ 相机只订阅 camera_info（小消息）而非 image_raw（640x480x3 反序列化很吃 CPU），
#:    图像本体留给 video.py 按需订阅 —— 这是"不看视频时几乎零开销"的关键。
HEALTH_ONLY = [
    ('/camera/color/camera_info', CameraInfo, 'sensor'),
    ('/map', OccupancyGrid, 'map'),
]


class StateCollector:
    """把话题/TF 收敛进 StateStore。所有回调都在 ROS 执行器线程里跑。"""

    #: /scan 落盘节流（秒）：激光 10Hz，但地图上不需要那么密，5Hz 足够且省带宽
    SCAN_STORE_INTERVAL = 0.2
    SCAN_MAX_POINTS = 180
    PLAN_MAX_POINTS = 200

    def __init__(self, node, store: StateStore,
                 map_frame: str = 'map', base_frame: str = 'base_footprint',
                 laser_frame: str = 'front_lidar_link'):
        self.node = node
        self.store = store
        self.map_frame = map_frame
        self.base_frame = base_frame
        self.laser_frame = laser_frame
        self._pose_src = None
        self._last_scan_store = 0.0

        # ── 状态话题 ──
        self._subs = []
        self._subs.append(node.create_subscription(
            Odometry, '/odom', self._on_odom, 10))
        self._subs.append(node.create_subscription(
            Twist, '/cmd_vel', self._on_cmd_vel, 10))
        self._subs.append(node.create_subscription(
            CarData, '/car_data', self._on_car_data, 10))
        self._subs.append(node.create_subscription(
            Control, '/arm_controller/position_info', self._on_arm, 10))
        self._subs.append(node.create_subscription(
            Int32, '/gripper/state', self._on_gripper, 10))
        self._subs.append(node.create_subscription(
            PoseWithCovarianceStamped, '/lidar_loc_pose', self._on_lidar_loc_pose, 10))
        self._subs.append(node.create_subscription(
            LaserScan, '/scan', self._on_scan, qos_profile_sensor_data))
        self._subs.append(node.create_subscription(
            Path, '/plan', self._on_plan, 10))
        self._subs.append(node.create_subscription(
            String, '/grape_harvest/status', self._on_task_status, 10))

        # ── 只做心跳的话题（避免订阅图像本体带来 CPU 开销）──
        for topic, meta in TOPIC_META.items():
            store.register_topic(topic, static=meta.get('static', False),
                                 hint_hz=meta.get('hint_hz'),
                                 timeout=meta.get('timeout'))
        for topic, msg_type, qos_kind in HEALTH_ONLY:
            qos = self._qos(qos_kind)
            self._subs.append(node.create_subscription(
                msg_type, topic, self._make_tick_cb(topic), qos))

        # ── /rosout → 日志面板 ──
        self._subs.append(node.create_subscription(
            Log, '/rosout', self._on_log, QoSProfile(
                depth=1000,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
            )))

        # ── TF: map → base_footprint（"机器人在地图里的坐标"正确来源）──
        self.tf_buffer = None
        self.tf_listener = None
        if _TF_OK:
            self.tf_buffer = Buffer()
            self.tf_listener = TransformListener(self.tf_buffer, node)
            self._tf_timer = node.create_timer(0.1, self._on_tf)   # 10Hz
        else:
            node.get_logger().warn('tf2_ros 不可用，地图坐标将回退到 /lidar_loc_pose')

    # ── QoS 选型 ──
    @staticmethod
    def _qos(kind: str):
        if kind == 'sensor':
            return qos_profile_sensor_data
        if kind == 'map':
            return QoSProfile(depth=1,
                              reliability=ReliabilityPolicy.RELIABLE,
                              durability=DurabilityPolicy.TRANSIENT_LOCAL)
        return 10

    def _make_tick_cb(self, topic: str):
        def _cb(_msg):
            self.store.tick(topic)
        return _cb

    # ── 回调 ──
    def _on_odom(self, msg: Odometry):
        self.store.tick('/odom')
        t = msg.twist.twist
        self.store.update(twist={'vx': r3(t.linear.x), 'vy': r3(t.linear.y),
                                 'vth': r3(t.angular.z)})

    def _on_cmd_vel(self, msg: Twist):
        self.store.tick('/cmd_vel')
        self.store.update(cmd_vel={'vx': r3(msg.linear.x), 'vy': r3(msg.linear.y),
                                   'vth': r3(msg.angular.z), 'age': 0.0})

    def _on_car_data(self, msg: CarData):
        self.store.tick('/car_data')
        self.store.update(
            battery={'voltage': round(float(msg.power_voltage), 2),
                     'charging': bool(msg.is_charge)},
            chassis={'motor_speed': [round(float(v), 1) for v in msg.motor_speed],
                     'crash': list(msg.crash),
                     'cliff': list(msg.cliff),
                     'smoke': int(msg.smoke),
                     'ultrasound': [round(float(v), 3) for v in msg.ultrasound]},
        )

    def _on_arm(self, msg: Control):
        self.store.tick('/arm_controller/position_info')
        self.store.update(arm={
            'x': r3(msg.position.x), 'y': r3(msg.position.y), 'z': r3(msg.position.z),
            'roll': round(deg(msg.roll), 1),
            'pitch': round(deg(msg.pitch), 1),
            'yaw': round(deg(msg.yaw), 1),
        })

    def _on_gripper(self, msg: Int32):
        self.store.tick('/gripper/state')
        pulse = int(msg.data)
        ratio = self.store.gripper_ratio(pulse)
        self.store.update(gripper={'pulse': pulse, 'ratio': round(ratio, 3),
                                   'closed': ratio < 0.5})

    def _on_task_status(self, msg: String):
        """采摘任务状态（JSON 字符串，由 harvest_node 发）。

        用 String+JSON 而不自定义 msg 的原因：fox_grape_harvest 是 ament_python 包，
        加消息类型要引入 rosidl 生成（需改成 ament_cmake），成本与风险都更高；
        而 WebUI 前端本来就是 JSON 生态，这样最直。
        """
        self.store.tick('/grape_harvest/status')
        raw = (msg.data or '').strip()
        if not raw:
            return
        try:
            task = json.loads(raw)
        except Exception:
            task = {'state': 'unknown', 'raw': raw[:200]}
        task['rx_ts'] = round(time.time(), 3)
        self.store.update(task=task)

    def _on_lidar_loc_pose(self, msg: PoseWithCovarianceStamped):
        self.store.tick('/lidar_loc_pose')
        if self._pose_src == 'tf':          # TF 可用时以 TF 为准
            return
        q = msg.pose.pose.orientation
        p = msg.pose.pose.position
        yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
        self.store.update(pose={
            'x': r3(p.x), 'y': r3(p.y), 'yaw': round(yaw, 4),
            'yaw_deg': round(deg(yaw), 1), 'src': 'lidar_loc',
        })

    def _on_tf(self):
        if self.tf_buffer is None:
            return
        try:
            tf = self.tf_buffer.lookup_transform(
                self.map_frame, self.base_frame, rclpy_time_zero())
        except (LookupException, ConnectivityException, ExtrapolationException):
            return
        except Exception:
            return
        tr = tf.transform.translation
        q = tf.transform.rotation
        yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
        self._pose_src = 'tf'
        self.store.update(pose={
            'x': r3(tr.x), 'y': r3(tr.y), 'yaw': round(yaw, 4),
            'yaw_deg': round(deg(yaw), 1), 'src': 'tf',
        })

    # ── 坐标变换（激光/路径 → map 系）──

    def _lookup_xyyaw(self, target: str, source: str):
        """查 TF target←source，返回 (x, y, yaw)；不可用返回 None。"""
        if self.tf_buffer is None:
            return None
        try:
            tf = self.tf_buffer.lookup_transform(target, source, rclpy_time_zero())
        except Exception:
            return None
        tr = tf.transform.translation
        q = tf.transform.rotation
        return (tr.x, tr.y, yaw_from_quaternion(q.x, q.y, q.z, q.w))

    def _on_scan(self, msg: LaserScan):
        """激光点转到 map 系并降采样（前端只需在图上看到障碍轮廓）。

        优先用 TF(laser→map) 保证与建图/代价地图一致；TF 未就绪时退回
        用机器人位姿近似（上电初期也能看到东西）。
        """
        self.store.tick('/scan')
        now = time.time()
        if now - self._last_scan_store < self.SCAN_STORE_INTERVAL:
            return
        self._last_scan_store = now

        base = self._lookup_xyyaw(self.map_frame, self.laser_frame)
        if base is None:
            pose = self.store.snapshot().get('pose')
            if pose is None:
                return
            base = (pose['x'], pose['y'], pose['yaw'])
        bx, by, byaw = base
        cos_b, sin_b = math.cos(byaw), math.sin(byaw)

        ranges = msg.ranges
        n = len(ranges)
        step = max(1, n // self.SCAN_MAX_POINTS)
        rmin = max(float(msg.range_min), 0.05)
        rmax = float(msg.range_max)
        pts = []
        for i in range(0, n, step):
            d = ranges[i]
            if not math.isfinite(d) or d < rmin or d > rmax:
                continue
            a = msg.angle_min + i * msg.angle_increment
            lx, ly = d * math.cos(a), d * math.sin(a)
            wx = bx + lx * cos_b - ly * sin_b
            wy = by + lx * sin_b + ly * cos_b
            pts.append([round(wx, 2), round(wy, 2)])
        self.store.update(scan={'frame': self.map_frame, 'points': pts, 'n': len(pts)})

    def _on_plan(self, msg: Path):
        """全局路径（绿线）降采样。"""
        self.store.tick('/plan')
        poses = msg.poses
        if not poses:
            self.store.update(plan={'points': [], 'n': 0, 'frames': 0})
            return
        step = max(1, len(poses) // self.PLAN_MAX_POINTS)
        pts = [[round(p.pose.position.x, 2), round(p.pose.position.y, 2)]
               for p in poses[::step]]
        self.store.update(plan={'points': pts, 'n': len(pts), 'frames': len(poses)})

    # /rosout 的 level: 10=DEBUG 20=INFO 30=WARN 40=ERROR 50=FATAL
    def _on_log(self, msg: Log):
        self.store.tick('/rosout')
        self.store.push_log(int(msg.level), msg.name, msg.msg)


def rclpy_time_zero():
    """lookup_transform 的"最新可用时刻"（避免多 import rclpy.time）。"""
    from rclpy.time import Time
    return Time()
