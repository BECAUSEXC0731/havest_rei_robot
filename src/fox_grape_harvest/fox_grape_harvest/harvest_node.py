"""
FOX 葡萄采摘主调度节点

综合流程:
  1. 加载 YAML 配置（航点、篮子位置、模型路径等）
  2. 遍历每个航点:
     a. 通过 Nav2 导航到目标点
     b. 到达后订阅 RGB-D 图像
     c. YOLO 检测葡萄
     d. 对每个检测到的葡萄:
        - 深度图 → 3D 坐标（相机 → 机器人坐标系）
        - 判断是否在机械臂工作空间内
        - 若不可达: 计算底盘微调量 → 移动底盘 → 重新检测
        - 执行抓取
     e. 导航到篮子位置 → 放置葡萄
  3. 返回地图原点

运行:
  ros2 run fox_grape_harvest grape_harvest_node \
    --ros-args -p config_file:=/path/to/harvest_config.yaml

  ⚠️ 注意：harvest_config.yaml 是【普通 YAML】（顶层直接是 yolo_model_path 等键），
  不能用 --params-file 传（ROS 参数文件必须带 /** / ros__parameters 结构，
  否则 rclpy.init 报 "Cannot have a value before ros__parameters"）；
  要传的是节点参数 config_file。

受控模式（WebUI / 任何外部调用）
--------------------------------
默认 **不自动开始**（start_on_boot:=false）。外部通过话题命令：

  发命令:  /grape_harvest/command   (std_msgs/String, JSON)
      {"cmd": "start"}                       ← 跑完整流程（航点遍历）
      {"cmd": "pick_one", "x":231,"y":178,"z":95}  ← 只抓一颗（最近的那颗）
      {"cmd": "pause"} / {"cmd": "resume"} / {"cmd": "stop"}

    命令行发（⚠️ 引号写法很关键）：
      ros2 topic pub --once /grape_harvest/command std_msgs/msg/String \
        'data: "{\"cmd\": \"start\"}"'
      不要写成 'data: {"cmd": "start"}' —— ros2 topic pub 会把 YAML 的 {} 当字典，
      转成 Python repr 字符串 "{'cmd': 'start'}"（单引号 = 非法 JSON），命令会被丢掉。
      单个词（pause/resume/stop）可直接用纯文本：'data: "stop"'

  看状态:  /grape_harvest/status    (std_msgs/String, JSON, 1Hz + 变化时立即发)
      {"state":"idle|running|paused|done|error", "stage":"...",
       "waypoint":0,"waypoints":2,"detected":3,"picked":1,"message":"..."}

为什么要这样改：原来启动 2s 后**无条件自动开跑**，一面网页刚打开、机械臂还在
旁边，机器就开始动了 —— 现场太危险。现在默认静止，必须显式下命令。
"""
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np
import yaml
import os
import json
import ast
import math
import time
import threading
from collections import deque

from fox_grape_harvest.yolo_detector import YoloDetector
from fox_grape_harvest.wait_utils import pump, set_external_spin, external_spin
from fox_grape_harvest.depth_utils import (
    load_hand_eye_calibration, depth_to_robot_3d, depth_to_robot_3d_stable,
    load_d2c_config, depth_to_robot_3d_d2c_stable,
    load_grasp_check, classify_reach, clamp_to_workspace
)
from fox_grape_harvest.arm_interface import ArmInterface
from fox_grape_harvest.chassis_interface import ChassisInterface


def parse_command(raw: str) -> dict:
    """把命令文本解析成命令 dict（模块级函数，便于单独测试）。

    兼容三种写法（都是实际会遇到的）：
      1) 合法 JSON：      '{"cmd": "start", "x": 1}'  ← WebUI / 引号写对的 ros2 topic pub
      2) Python repr：    "{'cmd': 'start'}"          ← ros2 topic pub 把 YAML 里的 {}
                                                          当字典后转成 repr（单引号=非法 JSON）
      3) 纯文本：         'start' / 'stop'            ← 命令行最省事的写法
    解析不出来就返回 {'cmd': 原文}，由调用方按“未知命令”处理。
    """
    try:
        req = json.loads(raw)
    except Exception:
        try:
            cand = ast.literal_eval(raw)
            req = cand if isinstance(cand, dict) else {'cmd': raw}
        except Exception:
            req = {'cmd': raw}
    return req if isinstance(req, dict) else {'cmd': raw}


class GrapeHarvestNode(Node):
    """葡萄采摘主控节点。"""

    def __init__(self):
        super().__init__('grape_harvest_node')

        # ── 加载配置 ──
        self.config = self._load_config()
        self.get_logger().info("✅ 配置已加载")

        # ── CvBridge ──
        self.bridge = CvBridge()

        # ── 相机数据 ──
        self.latest_rgb = None
        self.latest_depth = None
        self.depth_history = deque(maxlen=7)   # 最近几帧深度，取中值抗闪烁
        self.camera_matrix = None
        self.cam_info_received = False
        self.rgb_ready = False
        self.depth_ready = False
        self._img_lock = threading.Lock()

        # ── 手眼标定矩阵 (camera → robot) ──
        calib_path = self.config.get('hand_eye_calib_path',
                                     '/home/ubuntu/ros2fox/calib_result/hand_eye_result.json')
        self.T_cam_to_robot = load_hand_eye_calibration(calib_path)

        # ── 手动深度对齐配置 (彩色↔IR) ──
        d2c_path = self.config.get('d2c_extrinsic_path',
                                   '/home/ubuntu/ros2fox/calib_result/color_ir_extrinsic.json')
        ir_info_path = self.config.get('ir_camera_info_path',
                                       '/home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml')
        self.d2c = load_d2c_config(d2c_path, ir_info_path)
        if self.d2c is not None:
            self.K_ir, self.T_color_to_ir = self.d2c
            self.get_logger().info("✅ 已加载手动深度对齐配置 (彩色↔IR)")
        else:
            self.K_ir = None
            self.T_color_to_ir = None
            self.get_logger().warn(
                "⚠ 未找到手动对齐配置(color_ir_extrinsic.json)，深度按未对齐处理"
                "（需先跑 calibrate_color_ir.py 标定彩色↔IR 外参）")

        # ── 机械臂工作空间参数 ──
        arm_cfg = self.config.get('arm', {})
        self.ws_x_min = arm_cfg.get('workspace_x_min', 30)
        self.ws_x_max = arm_cfg.get('workspace_x_max', 320)
        self.ws_y_min = arm_cfg.get('workspace_y_min', -180)
        self.ws_y_max = arm_cfg.get('workspace_y_max', 180)
        self.ws_z_min = arm_cfg.get('workspace_z_min', 20)
        self.ws_z_max = arm_cfg.get('workspace_z_max', 200)
        self.preferred_x = arm_cfg.get('preferred_x', 200)
        self.preferred_y = arm_cfg.get('preferred_y', 0)
        self.preferred_z = arm_cfg.get('preferred_z', 130)
        # ── 可抓性判定参数（容度）：margin / 临界容差带 / 半径约束 / 自适应裕度 ──
        self.gc = load_grasp_check(self.config)
        # 临界可达(MARGINAL)是否也按“可抓”直接尝试（默认开，2026-09-24 用户要求）
        #   =1 → level 0/1 都直接抓；=0 → 只有 level 0 直接抓，level 1 先旋转微调
        self.grasp_marginal_level = 1 if bool(
            (arm_cfg.get('grasp_check', {}) or {}).get('grasp_marginal', True)) else 0
        self.ws_limits = {
            'x_min': self.ws_x_min, 'x_max': self.ws_x_max,
            'y_min': self.ws_y_min, 'y_max': self.ws_y_max,
            'z_min': self.ws_z_min, 'z_max': self.ws_z_max,
        }

        # ── 工具偏移补偿（机械臂局部系）+ 抓取过渡点（与 grape_grasp_test.py 一致）──
        self.tool_off = (arm_cfg.get('tool_offset_x', 0.0),
                         arm_cfg.get('tool_offset_y', 0.0),
                         arm_cfg.get('tool_offset_z', 0.0))
        # 过渡点（机械臂参考点，mm）：抓取前先到这里再去抓取点。
        # config 未配置 transition_* 时，自动取工作空间范围中点。
        _mid = (
            (self.ws_x_min + self.ws_x_max) / 2.0,
            (self.ws_y_min + self.ws_y_max) / 2.0,
            (self.ws_z_min + self.ws_z_max) / 2.0,
        )
        self.transition = (
            float(arm_cfg.get('transition_x', _mid[0])),
            float(arm_cfg.get('transition_y', _mid[1])),
            float(arm_cfg.get('transition_z', _mid[2])),
        )

        # ── 归位安全点（机械臂参考点，mm）──
        # 用 config 的 arm.home_x/y/z（与 grape_grasp_test.py / WebUI 直驱同一套参数，
        # 改 YAML 即可生效）；若三项没配齐则回落到 arm_controller 的 /home 服务
        # （那个位置是硬编码的，见 arm_swiftpro.cpp: goto_pos(200, 0, 150)）。
        _hx, _hy, _hz = (arm_cfg.get('home_x'), arm_cfg.get('home_y'), arm_cfg.get('home_z'))
        self.home_point = (None if None in (_hx, _hy, _hz)
                           else (float(_hx), float(_hy), float(_hz)))

        # ── 导航参数 ──
        nav_cfg = self.config.get('navigation', {})
        self.use_nav2 = nav_cfg.get('use_nav2', True)
        self.nav_timeout = nav_cfg.get('nav_timeout', 120.0)

        # ── 航点配置 ──
        self.waypoints = self.config.get('waypoints', [])
        self.return_to_origin = self.config.get('return_to_origin', True)

        # 到达航点后、开始检测前等待图像稳定的秒数（相机曝光/深度 + 底盘停稳需要时间）
        # 太短会拿到运动模糊帧 / 脏深度帧导致定位跳变，可用 config 的 image_settle_sec 调
        self.image_settle_sec = float(self.config.get('image_settle_sec', 4.0))

        # ── 车上篮子位置（机械臂坐标系 mm）：抓到葡萄后放到这里 ──
        basket_cfg = self.config.get('car_basket', {}) or {}
        self.car_basket_pos = basket_cfg.get(
            'position', {'x': 100.0, 'y': -120.0, 'z': 80.0})
        self.car_basket_lift = basket_cfg.get('lift_height', 30.0)

        # ── 相机订阅 ──
        rgb_topic = self.config.get('camera_rgb_topic', '/camera/color/image_raw')
        depth_topic = self.config.get('camera_depth_topic', '/camera/depth/image_raw')
        info_topic = self.config.get('camera_info_topic', '/camera/color/camera_info')

        self.create_subscription(
            Image, rgb_topic, self._rgb_callback, qos_profile_sensor_data)
        self.create_subscription(
            Image, depth_topic, self._depth_callback, qos_profile_sensor_data)
        # ⚠️ camera_info 也必须用 sensor QoS(BEST_EFFORT)：Orbbec 发布的是 BEST_EFFORT，
        #    订阅端用默认 RELIABLE 会“QoS 不兼容 → 一条都收不到”，
        #    表现就是卡在“等待相机内参”再终止（WebUI 那边同样踩过，见技术文档）
        self.create_subscription(
            CameraInfo, info_topic, self._info_callback, qos_profile_sensor_data)

        # ── YOLO 检测器 ──
        yolo_path = self.config.get('yolo_model_path', '')
        yolo_conf = self.config.get('yolo_confidence', 0.5)
        target_cls = self.config.get('target_class', 'grape')
        self.detector = None
        if yolo_path and os.path.exists(yolo_path):
            try:
                self.detector = YoloDetector(yolo_path, yolo_conf, target_cls)
                self.get_logger().info(f"✅ YOLO 检测器已加载: {yolo_path}")
            except Exception as e:
                self.get_logger().error(f"❌ YOLO 加载失败: {e}")
        else:
            self.get_logger().warn(f"⚠ YOLO 模型不存在: {yolo_path}，跳过检测")

        # ── 接口 ──
        self.arm = ArmInterface(self, grip_delay=arm_cfg.get('grip_delay', 1.0))
        self.chassis = ChassisInterface(self)

        chassis_cfg = self.config.get('chassis', {})
        # ── 旋转微调参数（见 config 的 chassis.rotate_*）──
        self.chassis.set_rotate_params(
            max_vth=chassis_cfg.get('rotate_max_vel', 0.5),
            min_vth=chassis_cfg.get('rotate_min_vel', 0.1),
            kp=chassis_cfg.get('rotate_kp', 1.5),
            tolerance_deg=chassis_cfg.get('rotate_tolerance_deg', 3.0),
            timeout=chassis_cfg.get('rotate_timeout', 15.0),
        )
        # ── 到点检测：多帧采样（2026-09-28）──
        # 到点（以及每次扫描旋转）后取几帧、逐帧检测，某帧里有可抓/临界就抓
        self.detect_frames = max(1, int(self.config.get('detect_frames', 3)))
        self.detect_frame_interval_sec = float(
            self.config.get('detect_frame_interval_sec', 0.3))
        # ── ±角度扫描（真不可达时，顺时针 → 逆时针 各转一次再找）──
        self.rotate_scan_deg = float(chassis_cfg.get('rotate_scan_deg', 25.0))
        # 每次扫描旋转后的等待（等车停稳 + 图像稳定再取帧）
        self.rotate_settle_sec = float(chassis_cfg.get('rotate_settle_sec', 3.0))
        # 航点一轮下来一颗都没抓到 → 是否做 ±角度扫描重试
        self.rotate_retry_enable = bool(chassis_cfg.get('rotate_retry_enable', True))
        # ── 兜底抓取（2026-09-28）：扫描后依然不可达 → 夹到最近可达点再试一次 ──
        self.fallback_nearest_enable = bool(arm_cfg.get('fallback_nearest', True))
        self.fallback_inward_mm = float(arm_cfg.get('fallback_inward_mm', 10.0))

        # ── 发布调试可视化 ──
        self.debug_pub = self.create_publisher(Image, '/grape_harvest/debug_image', 1)

        # ═══════════════ 受控化：状态/命令通道 ═══════════════
        # 默认不自启动：必须收到 /grape_harvest/command 的 start 才动
        self.start_on_boot = bool(self.declare_parameter('start_on_boot', False).value)
        self.auto_start_delay = float(self.declare_parameter('auto_start_delay', 2.0).value)
        cmd_topic = str(self.declare_parameter(
            'command_topic', '/grape_harvest/command').value)
        status_topic = str(self.declare_parameter(
            'status_topic', '/grape_harvest/status').value)

        self._run_lock = threading.Lock()
        self._running = False          # 是否有流程在跑（含单颗抓取）
        self._cancel = False           # 协作式取消：在检查点退出
        self._paused = False
        self._state = 'idle'
        self._stage = '待命'
        self._message = ''
        self._wp_index = 0
        self._detected = 0
        self._picked = 0
        self._started_at = 0.0
        self._hint = None              # pick_one 的目标点（机器人系 mm）

        self.status_pub = self.create_publisher(String, status_topic, 1)
        self.create_subscription(String, cmd_topic, self._on_command, 10)
        self.create_timer(1.0, self._publish_status)      # 心跳，1Hz
        self.get_logger().info(
            f"🎛  受控模式：start_on_boot={self.start_on_boot} "
            f"(命令 {cmd_topic} / 状态 {status_topic})"
            + ("" if self.start_on_boot else " —— 等外部下 start 命令"))

        if self.start_on_boot:
            # 保留旧行为（现场调试用）：延时等传感器就绪后自动开跑
            self.create_timer(self.auto_start_delay, self._auto_start)
        self._publish_status()

        self.get_logger().info("=" * 60)
        self.get_logger().info("🍇 FOX 葡萄采摘节点已初始化")
        self.get_logger().info(f"   航点数量: {len(self.waypoints)}")
        self.get_logger().info(f"   到点后等待图像稳定: {self.image_settle_sec:.1f}s")
        self.get_logger().info(f"   机械臂工作空间: X[{self.ws_x_min},{self.ws_x_max}] "
                               f"Y[{self.ws_y_min},{self.ws_y_max}] "
                               f"Z[{self.ws_z_min},{self.ws_z_max}]")
        self.get_logger().info(
            f"   工具偏移(mm): x={self.tool_off[0]:.0f} y={self.tool_off[1]:.0f} "
            f"z={self.tool_off[2]:.0f}")
        self.get_logger().info(
            f"   过渡点(mm,工作范围中点): x={self.transition[0]:.0f} "
            f"y={self.transition[1]:.0f} z={self.transition[2]:.0f}")
        if self.home_point is not None:
            self.get_logger().info(
                f"   归位安全点(config arm.home_*): x={self.home_point[0]:.0f} "
                f"y={self.home_point[1]:.0f} z={self.home_point[2]:.0f}")
        else:
            self.get_logger().info(
                "   归位安全点: 未配置 arm.home_* → 用 /home 服务 (200,0,150)")
        self.get_logger().info(
            f"   判定容度: margin_xy={self.gc['margin_xy_mm']:.0f} "
            f"margin_z={self.gc['margin_z_mm']:.0f} "
            f"容差带={self.gc['marginal_mm']:.0f}mm "
            f"临界也抓={bool(self.grasp_marginal_level)}")
        self.get_logger().info(
            f"   多帧检测: {self.detect_frames} 帧 / 间隔 {self.detect_frame_interval_sec:.2f}s")
        self.get_logger().info(
            f"   ±角度扫描: ±{self.rotate_scan_deg:.0f}° "
            f"扫描后等 {self.rotate_settle_sec:.1f}s "
            f"上限 {self.chassis.rotate_max_vel:.2f}rad/s "
            f"容差 {math.degrees(self.chassis.rotate_tolerance):.1f}° "
            f"超时 {self.chassis.rotate_timeout:.0f}s "
            f"开关={self.rotate_retry_enable}")
        self.get_logger().info(
            f"   兜底抓取: {'开' if self.fallback_nearest_enable else '关'}"
            f"（不可达 → 夹到最近可达点，向内收 {self.fallback_inward_mm:.0f}mm）")
        self.get_logger().info(f"   YOLO 模型: {yolo_path}")
        self.get_logger().info("=" * 60)

    # ═══════════════════════ 回调 ═══════════════════════

    def _info_callback(self, msg: CameraInfo):
        if self.cam_info_received:
            return
        k = np.array(msg.k).reshape(3, 3)
        if k[0, 0] == 0 or np.any(np.isnan(k)):
            return
        self.camera_matrix = k
        self.cam_info_received = True
        self.get_logger().info(f"✅ 相机内参已加载: fx={k[0,0]:.1f}, fy={k[1,1]:.1f}")

    def _rgb_callback(self, msg: Image):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            with self._img_lock:
                self.latest_rgb = cv_img
                self.rgb_ready = True
        except Exception as e:
            self.get_logger().warn(f"RGB 转换失败: {e}")

    def _depth_callback(self, msg: Image):
        try:
            # 深度图可能是 32FC1 (米) 或 16UC1 (厘米!)——本相机 16UC1 单位是 cm，/100 转米
            depth_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if depth_img.dtype == np.uint16:
                depth_img = depth_img.astype(np.float32) / 100.0
            elif depth_img.dtype == np.float32:
                pass  # 已经是米
            with self._img_lock:
                self.latest_depth = depth_img
                self.depth_history.append(depth_img)
                self.depth_ready = True
        except Exception as e:
            self.get_logger().warn(f"深度图转换失败: {e}")

    # ═══════════════════════ 受控化：状态与命令 ═══════════════════════

    def _publish_status(self) -> None:
        """发布状态 JSON（1Hz + 状态变化时立即发，供 WebUI 显示）。"""
        try:
            msg = String()
            msg.data = json.dumps({
                'state': self._state,
                'stage': self._stage,
                'message': self._message,
                'waypoint': self._wp_index,
                'waypoints': len(self.waypoints),
                'detected': self._detected,
                'picked': self._picked,
                'running': self._running,
                'paused': self._paused,
                'elapsed_s': round(time.time() - self._started_at, 1) if self._started_at else 0.0,
            }, ensure_ascii=False)
            self.status_pub.publish(msg)
        except Exception:
            pass

    def _set_stage(self, stage: str, state: str | None = None,
                   message: str = '') -> None:
        """更新阶段并立即上报（同时打日志，方便 /rosout 面板看到）。"""
        self._stage = stage
        if state:
            self._state = state
        self._message = message
        self.get_logger().info(f"🎛  [{self._state}] {stage}" + (f" — {message}" if message else ''))
        self._publish_status()

    def _pump(self, dt: float = 0.05) -> None:
        """推进一次回调处理。

        ⚠️ 流程现在跑在 **worker 线程**，主线程的 MultiThreadedExecutor 一直在 spin，
        所以这里只需 sleep（详见 wait_utils 里的实测数据与说明）。
        """
        pump(self, dt)

    def _wait_if_paused(self) -> None:
        """暂停等待（期间继续 spinner，以便收到 resume/stop）。"""
        if not self._paused:
            return
        self._set_stage('已暂停', 'paused')
        while self._paused and not self._cancel:
            self._pump(0.1)

    def _pump_while(self, seconds: float, step: float = 0.05) -> None:
        """可被取消/暂停打断的 sleep（替代 time.sleep，保证指令及时生效）。"""
        end = time.time() + seconds
        while time.time() < end and not self._cancel:
            self._pump(step)
            self._wait_if_paused()

    def _on_command(self, msg: String) -> None:
        """命令入口（JSON）。"""
        raw = (msg.data or '').strip()
        if not raw:
            return
        req = parse_command(raw)
        cmd = str(req.get('cmd', '')).lower()
        self.get_logger().info(f"🎛  收到命令: {cmd or req}")

        if cmd == 'stop':
            self._paused = False
            self._cancel_nav()
            if self._running:
                self._cancel = True
                self._set_stage('正在停止（当前动作完成后退出）', 'running', '收到 stop')
            else:
                # 空闲时收到 stop：不要停在"正在停止"上，直接回到待命
                self._cancel = False
                self._set_stage('待命', 'idle', '当前没有任务在跑')
            return
        if cmd == 'pause':
            self._paused = True
            return
        if cmd == 'reload':
            # WebUI 在“保存抓取点补偿”后会发这条：让跑着的流程也吃上新配置
            self._reload_config()
            return
        if cmd == 'resume':
            self._paused = False
            self._set_stage('继续', 'running')
            return
        if cmd in ('start', 'pick_one'):
            if self._running:
                self._set_stage(self._stage, message='已有流程在跑，忽略本次命令')
                return
            self._cancel = False
            self._paused = False
            self._hint = None
            if cmd == 'pick_one':
                try:
                    self._hint = (float(req.get('x')), float(req.get('y')), float(req.get('z')))
                except Exception:
                    self._hint = None           # 没给坐标 → 抓最近的一颗
            self._running = True
            self._started_at = time.time()
            self._picked = 0
            self._detected = 0
            # ⚠️ 必须在 worker 线程里跑：流程里全是阻塞调用，
            #    若在回调里同步跑，executor 无法再处理 stop/pause（实测只能收到 1/3 条命令）
            self._worker = threading.Thread(
                target=self._run_workflow_thread, name='harvest-worker', daemon=True)
            self._worker.start()
            return
        self.get_logger().warn(f"🎛  未知命令: {cmd}")

    def _run_workflow_thread(self) -> None:
        """worker 线程主体：跑流程，结束后把 running 复位。"""
        try:
            if self._hint is not None:
                self._run_pick_one()
            else:
                self._run_harvest_workflow()
        except Exception as exc:               # 不让异常静默吞掉
            self.get_logger().error(f"❌ 流程异常: {exc!r}")
            self._set_stage('流程异常终止', 'error', repr(exc))
        finally:
            self._running = False
            self._hint = None
            self._cancel = False
            self._publish_status()

    def _cancel_nav(self) -> None:
        """停止时顺便取消正在进行的 Nav2 目标（否则车会继续跑完导航）。"""
        try:
            gh = getattr(self.chassis, '_active_goal', None)
            if gh is not None:
                gh.cancel_goal_async()
                self.get_logger().info("🎛  已取消当前导航目标")
        except Exception as exc:
            self.get_logger().warn(f"🎛  取消导航失败: {exc}")

    def _reload_config(self) -> None:
        """重读 harvest_config.yaml 并刷新“可在线调”的参数（WebUI 保存补偿后调用）。

        只刷新不需要重建订阅/接口的部分：工具偏移、过渡点、夹紧延时、可抓性容度、
        工作空间盒、篮子位置、航点。这样在页面调完补偿后，一键采摘也能立即用新值。
        """
        try:
            cfg = self._load_config()
        except Exception as exc:
            self.get_logger().error(f"重读配置失败: {exc}")
            return
        if not cfg:
            self.get_logger().warn("重读配置为空，保持原值")
            return
        self.config = cfg
        arm_cfg = cfg.get('arm', {}) or {}
        self.ws_x_min = arm_cfg.get('workspace_x_min', self.ws_x_min)
        self.ws_x_max = arm_cfg.get('workspace_x_max', self.ws_x_max)
        self.ws_y_min = arm_cfg.get('workspace_y_min', self.ws_y_min)
        self.ws_y_max = arm_cfg.get('workspace_y_max', self.ws_y_max)
        self.ws_z_min = arm_cfg.get('workspace_z_min', self.ws_z_min)
        self.ws_z_max = arm_cfg.get('workspace_z_max', self.ws_z_max)
        self.ws_limits = {'x_min': self.ws_x_min, 'x_max': self.ws_x_max,
                          'y_min': self.ws_y_min, 'y_max': self.ws_y_max,
                          'z_min': self.ws_z_min, 'z_max': self.ws_z_max}
        self.gc = load_grasp_check(cfg)
        self.tool_off = (arm_cfg.get('tool_offset_x', self.tool_off[0]),
                         arm_cfg.get('tool_offset_y', self.tool_off[1]),
                         arm_cfg.get('tool_offset_z', self.tool_off[2]))
        _mid = ((self.ws_x_min + self.ws_x_max) / 2.0,
                (self.ws_y_min + self.ws_y_max) / 2.0,
                (self.ws_z_min + self.ws_z_max) / 2.0)
        self.transition = (float(arm_cfg.get('transition_x', _mid[0])),
                           float(arm_cfg.get('transition_y', _mid[1])),
                           float(arm_cfg.get('transition_z', _mid[2])))
        self.arm.grip_delay = arm_cfg.get('grip_delay', self.arm.grip_delay)
        basket_cfg = cfg.get('car_basket', {}) or {}
        if basket_cfg:
            self.car_basket_pos = basket_cfg.get('position', self.car_basket_pos)
            self.car_basket_lift = basket_cfg.get('lift_height', self.car_basket_lift)
        if cfg.get('waypoints'):
            self.waypoints = cfg['waypoints']
        self.get_logger().info(
            f"🔄 已重读配置: tool_offset=({self.tool_off[0]:.0f},{self.tool_off[1]:.0f},"
            f"{self.tool_off[2]:.0f}) 过渡点=({self.transition[0]:.0f},"
            f"{self.transition[1]:.0f},{self.transition[2]:.0f}) "
            f"夹紧延时={self.arm.grip_delay:.1f}s")
        self._set_stage('已重读配置', self._state)

    def _run_pick_one(self) -> None:
        """只抓一颗（WebUI 检测列表点选）：
        用与完整流程**完全相同**的检测+抓取+放篮代码，只是限制只抓 1 颗、
        并且优先抓离 hint（页面选中那颗）最近的目标。
        """
        self._set_stage('单颗抓取：等待相机内参', 'running')
        if not self._wait_camera_info(15.0):
            self._set_stage('单颗抓取失败', 'error', '未收到相机内参')
            return
        self._set_stage('单颗抓取：检测 + 抓取')
        n = self._detect_and_pick(limit=1, hint=self._hint)
        self._picked += n
        if n:
            self._set_stage('单颗抓取完成', 'done', f'抓取 {n} 颗')
        else:
            self._set_stage('单颗抓取结束', 'error', '未抓到（目标不可达/未检测到）')

    def _wait_camera_info(self, timeout_s: float) -> bool:
        if self.cam_info_received:
            return True
        deadline = time.time() + timeout_s
        while time.time() < deadline and not self._cancel:
            self._pump(0.2)
            if self.cam_info_received:
                return True
        return self.cam_info_received

    def _arm_home(self, timeout_sec: float | None = None) -> bool:
        """机械臂归位（任务开始/结束、退出时都走这里）。

        优先用 config 的 ``arm.home_x/y/z``（与脚本/WebUI 同一套参数，改 YAML 即可调）；
        没配置则回落到 arm_controller 的 ``/home`` 服务。

        timeout_sec: 单次动作等待上限；退出清理会传小值，避免服务没起时挂 30~60s。
        """
        if self.home_point is None:
            self.get_logger().warn(
                "⚠ 未配置 arm.home_x/y/z，回落到 /home 服务（硬编码 200,0,150）")
            return self.arm.home(timeout_sec=timeout_sec)

        hx, hy, hz = self.home_point
        self.get_logger().info(f"🛡 归位到 config 安全点: ({hx:.0f}, {hy:.0f}, {hz:.0f})")
        if self.arm.goto(hx, hy, hz, timeout_sec=timeout_sec):
            return True
        self.get_logger().warn(
            f"⚠ 安全点 ({hx:.0f}, {hy:.0f}, {hz:.0f}) 不可达，回落到 /home 服务")
        return self.arm.home(timeout_sec=timeout_sec)

    # ═══════════════════════ 主流程 ═══════════════════════

    def _auto_start(self):
        """启动后自动跑一次（仅 start_on_boot:=true 时注册这个定时器）。"""
        # Humble 的 create_timer 不支持 oneshot 参数，用手动取消实现单次触发
        self._start_timer = self.create_timer(0.0, self._auto_start_once)

    def _auto_start_once(self):
        """定时器回调：取消定时器后把主流程丢到 worker 线程（只触发一次）。"""
        if self._start_timer is not None:
            self._start_timer.cancel()
        if self._running:
            return
        self._running = True
        self._started_at = time.time()
        self._worker = threading.Thread(
            target=self._run_workflow_thread, name='harvest-worker', daemon=True)
        self._worker.start()

    def _run_harvest_workflow(self):
        """主采摘工作流（受控：每步都检查 _cancel/_paused）。"""
        self.get_logger().info("\n" + "=" * 60)
        self.get_logger().info("🍇 开始葡萄采摘工作流")
        self.get_logger().info("=" * 60)

        self._set_stage('等待相机内参', 'running')
        if not self._wait_camera_info(20.0):
            self._set_stage('启动失败', 'error', '未收到相机内参')
            return
        if self._cancel:
            self._set_stage('已取消', 'idle', '启动前被取消')
            return

        # 机械臂归位（config 的 arm.home_* 安全点，见 _arm_home）
        self._set_stage('机械臂归位')
        self.get_logger().info("🔄 机械臂归位...")
        self._arm_home()

        grape_count = 0

        for i, wp in enumerate(self.waypoints):
            if self._cancel:
                break
            self._wp_index = i
            self._set_stage(f'导航到航点 {i+1}/{len(self.waypoints)}：'
                            f"{wp.get('description', '')}")
            self.get_logger().info(f"\n{'─'*60}")
            self.get_logger().info(f"📍 航点 {i+1}/{len(self.waypoints)}: "
                                   f"{wp.get('description', '')}")
            self.get_logger().info(f"   位置: ({wp['position']['x']:.2f}, {wp['position']['y']:.2f})")
            self.get_logger().info(f"{'─'*60}")

            # 步骤 1: 导航到航点
            if not self._navigate_to_waypoint(wp):
                self.get_logger().warn(f"⚠ 航点 {i+1} 导航失败，跳过")
                continue
            if self._cancel:
                break

            # 步骤 2: 等待图像稳定（可被打断；默认 4s，见 config image_settle_sec）
            self._set_stage('等待图像稳定', message=f'{self.image_settle_sec:.1f}s')
            self._pump_while(self.image_settle_sec)

            # 步骤 3: 检测 + 抓取（每抓到一颗立即放到车上篮子）
            self._set_stage('检测 + 抓取')
            picked = self._detect_and_pick()

            # 步骤 4: 本航点一颗都没抓到 → ±角度扫描（先顺时针，再逆时针）重找
            #          （config: chassis.rotate_retry_enable / rotate_scan_deg）
            if picked == 0 and not self._cancel:
                picked += self._scan_rotate_search()

            # 步骤 5: 扫描后依然不可达 → 兜底：夹到工作空间内最近的可达点再抓一次
            #          （config: arm.fallback_nearest / fallback_inward_mm）
            if picked == 0 and not self._cancel:
                picked += self._fallback_grasp_nearest()

            grape_count += picked
            self._picked += picked

            self.get_logger().info(f"  本航点已摘取 {picked} 颗葡萄")

        # 所有航点已遍历完，没有剩余导航点了 → 返回原点（篮子随车带走）
        if self.return_to_origin and not self._cancel:
            self._set_stage('返回地图原点')
            self.get_logger().info(f"\n{'─'*60}")
            self.get_logger().info(f"🏠 采摘结束，返回地图原点")
            self.get_logger().info(f"{'─'*60}")
            self._navigate_to_pose(0.0, 0.0, 0.0, 1.0)

        # 机械臂归位
        self._set_stage('机械臂归位')
        self._arm_home()

        if self._cancel:
            self._set_stage('已停止', 'idle', f'共摘取 {grape_count} 颗（用户停止）')
            self._cancel = False            # 已回到安全态，清标志
        else:
            self._set_stage('采摘完成', 'done', f'共摘取 {grape_count} 颗葡萄')
        self.get_logger().info("\n" + "=" * 60)
        self.get_logger().info(f"🎉 采摘完成！共摘取 {grape_count} 颗葡萄")
        self.get_logger().info("=" * 60)

    def _navigate_to_waypoint(self, wp: dict) -> bool:
        """导航到单个航点。"""
        pos = wp['position']
        orient = wp.get('orientation', {})
        return self._navigate_to_pose(
            pos['x'], pos['y'],
            orient.get('z', 0.0),
            orient.get('w', 1.0),
        )

    def _navigate_to_pose(self, x: float, y: float,
                          oz: float = 0.0, ow: float = 1.0) -> bool:
        """导航到指定坐标。"""
        if self.use_nav2:
            return self.chassis.navigate_to(x, y, oz, ow, timeout_sec=self.nav_timeout)
        else:
            self.get_logger().warn("手动模式导航未实现")
            return False

    # ═══════════════════════ 检测 + 抓取 ═══════════════════════

    def _det_robot_pos(self, det: dict, depth):
        """一个检测框 → 机器人坐标系 3D 坐标（mm）。

        跨帧取深度中值抗闪烁；有手动 D2C 标定就走 D2C（否则走未对齐）。
        抽成函数是为了 pick_one 选“离页面选中那颗最近的目标”时复用同一套计算。
        """
        cx, cy = det['center']
        with self._img_lock:
            frames = [f.copy() for f in self.depth_history] or [depth]
        if self.T_color_to_ir is not None:
            return depth_to_robot_3d_d2c_stable(
                cx, cy, frames, self.camera_matrix, self.K_ir,
                self.T_color_to_ir, self.T_cam_to_robot)
        return depth_to_robot_3d_stable(
            cx, cy, frames, self.camera_matrix, self.T_cam_to_robot)

    def _detect_and_pick(self, limit: int | None = None, hint=None) -> int:
        """到点后的检测 + 抓取（**多帧采样版**，2026-09-28 用户要求）。

        取 `detect_frames` 帧（帧间隔 detect_frame_interval_sec），逐帧 YOLO：
          · 某帧里出现 可抓(GRASP) 或 临界(MARGINAL) 目标 → 就在该帧上逐个抓取，然后收工；
          · 所有帧都只有 真不可达(UNREACHABLE) 目标 → 返回 0
            （由调用方 `_scan_rotate_search()` 决定要不要 ±角度扫描重找）。

        Args:
            limit: 最多抓几颗（None = 全抓；pick_one 传 1）
            hint:  (x,y,z) mm —— 只抓离它最近的那颗（WebUI 列表点选用）
        Returns:
            已摘取的数量
        """
        if self.detector is None:
            self.get_logger().warn("无 YOLO 检测器，跳过检测")
            return 0

        picked = 0
        for k in range(self.detect_frames):
            if self._cancel:
                break
            if limit is not None and picked >= limit:
                break
            if k > 0:
                # 等新帧到（多帧采样：抗单帧闪烁 / 误检）
                self._pump_while(self.detect_frame_interval_sec)

            rgb, depth = self._get_synced_frames()
            if rgb is None or depth is None:
                self.get_logger().warn("未获取到图像帧")
                continue

            detections = self.detector.detect(rgb)
            self._detected = len(detections)
            self.get_logger().info(
                f"🔍 第 {k+1}/{self.detect_frames} 帧：检测到 {len(detections)} 个目标")
            if not detections:
                continue

            # 指定了目标点 → 只保留最近的那一颗（页面点选与主流程共用同一抓取路径）
            if hint is not None:
                best, best_d = None, float('inf')
                for i, det in enumerate(detections):
                    p, _ = self._det_robot_pos(det, depth)
                    if p is None:
                        continue
                    d = sum((p[k] - hint[k]) ** 2 for k in range(3))
                    if d < best_d:
                        best, best_d = i, d
                if best is None:
                    self.get_logger().warn("指定目标附近没有可定位的检测框")
                    continue
                self.get_logger().info(
                    f"  🎯 选中离页面选点最近的检测框 #{best}（距离 {math.sqrt(best_d):.0f}mm）")
                detections = [detections[best]]

            # 先判一遍：本帧有没有 可抓 / 临界 目标？
            n_ok = 0
            for det in detections:
                pt, _ = self._det_robot_pos(det, depth)
                if pt is None:
                    continue
                lvl, _code = self._reach_level(*pt)
                if lvl <= self.grasp_marginal_level:
                    n_ok += 1
            if n_ok == 0:
                self.get_logger().info("  本帧没有可抓/临界目标 → 换下一帧")
                continue

            self.get_logger().info(f"  ✅ 本帧有 {n_ok} 个可抓/临界目标 → 开始抓取")
            picked += self._grasp_from_frame(rgb, depth, detections, limit=limit)
            if picked > 0:
                break          # 抓到了就不再找别的帧

        return picked

    def _grasp_from_frame(self, rgb, depth, detections, limit: int | None = None) -> int:
        """在一帧的检测结果上逐个抓取。

        分级 ≤ grasp_marginal_level（可抓 / 临界）→ 直接抓；
        真不可达(UNREACHABLE) → 只打日志跳过（改由航点级 ±角度扫描重找）。
        """
        # 发布调试图像
        debug_img = self.detector.draw_detections(rgb, detections)
        self._publish_debug_image(debug_img)

        picked = 0
        for idx, det in enumerate(detections):
            if self._cancel:
                self.get_logger().info("  ⏹ 收到停止命令，停止抓取")
                break
            if limit is not None and picked >= limit:
                break
            self._wait_if_paused()
            self._set_stage(f'抓取目标 {idx+1}/{len(detections)}')
            self.get_logger().info(f"\n  ── 目标 {idx+1}/{len(detections)} ──")
            cx, cy = det['center']

            # 获取 3D 位置（机器人坐标系，毫米）——跨帧取中值抗深度闪烁
            pt_robot_mm, depth_m = self._det_robot_pos(det, depth)
            if pt_robot_mm is None:
                self.get_logger().warn(f"  深度无效 (像素 {cx},{cy})，跳过")
                continue

            rx, ry, rz = pt_robot_mm
            self.get_logger().info(f"  葡萄位置 (机器人坐标系): "
                                   f"({rx:.0f}, {ry:.0f}, {rz:.0f}) mm")

            # 检查是否在机械臂工作空间内（分级: 可达 / 临界可达 / 不可达）
            # 2026-09-24: 临界可达(MARGINAL)也当“可抓”直接尝试（grasp_check.grasp_marginal）
            # 2026-09-28: 真不可达(UNREACHABLE)不再做“对准方位”的旋转，
            #             改由整个航点级的 ±角度扫描重找（_scan_rotate_search）
            level, code = self._reach_level(rx, ry, rz)

            if level <= self.grasp_marginal_level:
                if level == 0:
                    self.get_logger().info("  ✅ 机械臂可直接到达")
                else:
                    self.get_logger().info(
                        f"  ✅ 临界可达({code})，按可抓处理 → 直接尝试抓取")
            else:
                self.get_logger().warn(
                    f"  ⚠ 真不可达({code})，本帧跳过（整轮结束后做 ±角度扫描）")
                continue

            # 执行抓取
            success = self._pick_grape(rx, ry, rz)
            if success:
                picked += 1
                # 抓到后立即把机械臂移到车上篮子并松开
                self._place_to_car_basket()
            else:
                self.get_logger().warn("  ❌ 抓取失败")

        return picked
    def _get_synced_frames(self):
        """获取一组同步的 RGB 和深度帧。"""
        with self._img_lock:
            if self.latest_rgb is None or self.latest_depth is None:
                return None, None
            rgb = self.latest_rgb.copy()
            depth = self.latest_depth.copy()
        return rgb, depth

    def _publish_debug_image(self, cv_image):
        """发布调试图像（可在 RViz 中查看）。"""
        try:
            msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
            self.debug_pub.publish(msg)
        except Exception:
            pass

    # ═══════════════════════ 工作空间判断 ═══════════════════════

    def _reach_level(self, x_mm: float, y_mm: float, z_mm: float):
        """可抓性分级：返回 (level, code)。0=GRASP / 1=MARGINAL / 2=NO。

        判定只用"工作空间盒 + 可选半径/自适应裕度"，不参与 3D 计算，
        因此放宽判定容度不会损失定位精度。
        """
        return classify_reach(x_mm, y_mm, z_mm, self.ws_limits, self.gc)

    def _scan_rotate_search(self) -> int:
        """真不可达时的 ±角度扫描重找（2026-09-28 用户要求）。

        顺序：
          ① **顺时针**转 `rotate_scan_deg` → 等 `rotate_settle_sec` → 多帧检测
             → 有可抓/临界就直接抓；
          ② 仍没有 → 再**逆时针**转 2×`rotate_scan_deg`
             （净效果 = 停在原点位的另一侧，即 +`rotate_scan_deg`）
             → 同样等稳定 + 多帧检测 → 有就抓。

        为什么要转：葡萄在机器人系的坐标会随车头朝向一起转（变为 (r, ψ−Δθ)），
        所以"距离够但方位偏出盒外"的目标，转到另一侧就落进可抓范围了。

        Returns: 本轮扫描一共抓到的数量
        """
        if not self.rotate_retry_enable:
            return 0

        total = 0
        steps = ((-self.rotate_scan_deg, '顺时针'), (2.0 * self.rotate_scan_deg, '逆时针'))
        for delta_deg, label in steps:
            if self._cancel or total > 0:
                break
            self._set_stage(f'扫描：{label} {abs(delta_deg):.0f}°')
            self.get_logger().warn(
                f"⚠ 本点没有可抓/临界目标 → {label}转 {abs(delta_deg):.0f}° 后再找一次")
            if not self.chassis.rotate_by(math.radians(delta_deg)):
                self.get_logger().warn(f"  ⚠ {label}旋转失败，跳过这一步")
                continue
            # 等车停稳 + 图像稳定
            self._set_stage(f'{label}后等待 {self.rotate_settle_sec:.1f}s')
            self.get_logger().info(f"  ⏳ {label}后等待 {self.rotate_settle_sec:.1f}s…")
            self._pump_while(self.rotate_settle_sec)
            # 多帧检测 + 抓取
            total += self._detect_and_pick()

        if total == 0:
            self.get_logger().warn("  ⚠ ±角度扫描都没找到可抓/临界目标，本航点结束")
        return total

    def _fallback_grasp_nearest(self) -> int:
        """兜底抓取（2026-09-28）：±角度扫描后依然不可达 → 夹到**最近的可达点**去抓。

        做法：
          1. 多帧检测，把每个"真不可达"的可定位目标用 `clamp_to_workspace()`
             夹到工作空间内（逐轴夹到边界，再向内收 ``fallback_inward_mm``）；
          2. 挑**夹取代价 moved_mm 最小**的那个（= 离可达域最近的那颗葡萄）；
          3. 直接以夹取后的点走同一套 `_pick_grape()` + 放篮流程（只试这一个点）。

        ⚠️ 这是"够不到也把手伸到最接近的位置试试"的兜底：
           葡萄离夹取点最多差 moved_mm，可能夹空/夹偏。
           开关 `arm.fallback_nearest`（默认开），内收量 `arm.fallback_inward_mm`。
        Returns: 抓到数量（0 或 1）
        """
        if not self.fallback_nearest_enable or self.detector is None:
            return 0

        best = None
        for k in range(self.detect_frames):
            if self._cancel:
                return 0
            if k > 0:
                self._pump_while(self.detect_frame_interval_sec)
            rgb, depth = self._get_synced_frames()
            if rgb is None or depth is None:
                continue
            detections = self.detector.detect(rgb)
            self.get_logger().info(
                f"  🔍 兜底：第 {k+1}/{self.detect_frames} 帧 {len(detections)} 个目标")
            for det in detections:
                pt, _ = self._det_robot_pos(det, depth)
                if pt is None:
                    continue
                x, y, z = pt
                lvl, code = self._reach_level(x, y, z)
                if lvl <= self.grasp_marginal_level:
                    continue            # 本来就可抓的（理论上轮不到兜底）
                cx, cy, cz, moved = clamp_to_workspace(
                    x, y, z, self.ws_limits, self.gc, self.fallback_inward_mm)
                if best is None or moved < best[0]:
                    best = (moved, x, y, z, cx, cy, cz, code)
            if best is not None and best[0] <= 0.0:
                break                   # 已经正好落在可达域内，不必再取帧

        if best is None:
            self.get_logger().warn("  ⚠ 兜底：多帧都没有可定位的不可达目标，放弃")
            return 0

        moved, x, y, z, cx, cy, cz, code = best
        self._set_stage(f'兜底抓取（夹到最近可达点，偏 {moved:.0f}mm）')
        self.get_logger().warn(
            f"  🪄 兜底：目标 ({x:.0f}, {y:.0f}, {z:.0f}) {code} 不可达 "
            f"→ 夹到最近可达点 ({cx:.0f}, {cy:.0f}, {cz:.0f})，偏离 {moved:.0f}mm")
        if self._pick_grape(cx, cy, cz):
            self._place_to_car_basket()
            return 1
        self.get_logger().warn("  ❌ 兜底抓取失败")
        return 0

    # （_rotate_retry_once / _normalize_angle 已于 2026-09-28 删除：
    #   原来“把葡萄方位对准正前方”的思路被 _scan_rotate_search 的 ±角度扫描取代）

    # ═══════════════════════ 抓取/放置执行 ═══════════════════

    def _tool_offset_robot(self, x: float, y: float, z: float):
        """把夹爪【局部坐标系】偏移旋转到机器人坐标系（与 grape_grasp_test.py 一致）。

        局部系定义（机械臂基座为原点）:
          tool_offset_x: 沿机械臂指向目标的径向方向
          tool_offset_y: 侧向（垂直径向，向左为正）
          tool_offset_z: 垂直方向（不受朝向影响）
        机械臂朝向 θ = atan2(y, x)。
        """
        ox_l, oy_l, oz_l = self.tool_off
        theta = math.atan2(y, x)
        c, s = math.cos(theta), math.sin(theta)
        ox_r = ox_l * c - oy_l * s
        oy_r = ox_l * s + oy_l * c
        return ox_r, oy_r, oz_l

    def _pick_grape(self, x_mm: float, y_mm: float, z_mm: float) -> bool:
        """
        在目标位置执行葡萄抓取（夹爪），与 grape_grasp_test.py 同流程:
          1. 先到过渡点（工作空间范围中点）
          2. 直接到工具偏移补偿后的抓取位置（无预定位抬升/下降）
          3. 夹爪夹紧（不抬升，交给放篮流程）
        """
        # 工具偏移补偿: 葡萄坐标 + 旋转到机器人系的夹爪偏移 → 机械臂参考点目标
        ox, oy, oz = self._tool_offset_robot(x_mm, y_mm, z_mm)
        gx = x_mm + ox
        gy = y_mm + oy
        gz = z_mm + oz
        tx, ty, tz = self.transition
        self.get_logger().info(
            f"\n  🦾 抓取葡萄: ({x_mm:.0f}, {y_mm:.0f}, {z_mm:.0f}) → "
            f"参考点({gx:.0f}, {gy:.0f}, {gz:.0f})")

        # 1. 先到过渡点（工作空间范围中点）
        self._set_stage('机械臂 → 过渡点')
        self.get_logger().info(f"  ↗ 过渡点: ({tx:.0f}, {ty:.0f}, {tz:.0f})")
        if not self.arm.goto(tx, ty, tz):
            self.get_logger().warn("  过渡点不可达")
            return False
        self._pump_while(0.5)
        if self._cancel:                       # 已收到停止：不要继续往葡萄伸
            self.get_logger().warn("  ⏹ 停止命令：放弃本次抓取")
            return False

        # 2. 直接到补偿后的抓取位置（不先到安全高度）
        self._set_stage('机械臂 → 抓取点')
        self.get_logger().info(f"  → 抓取位置: ({gx:.0f}, {gy:.0f}, {gz:.0f})")
        if not self.arm.goto(gx, gy, gz):
            self.get_logger().warn("  抓取位置不可达")
            return False
        self._pump_while(0.5)

        # 3. 夹爪夹紧
        self._set_stage('夹爪夹紧')
        if not self.arm.grip(True):
            self.get_logger().warn("  夹爪夹紧失败")
            return False
        self._pump_while(float(self.arm.grip_delay))
        self.get_logger().info("  ✅ 抓取成功！")
        return True

    def _place_to_car_basket(self):
        """
        把机械臂夹住的葡萄放到车上的篮子。
        篮子放在底盘上（随车走），使用配置 car_basket.position
        （机械臂坐标系 mm）直接移动到位后松开夹爪，无需导航。
        """
        pos = self.car_basket_pos
        place_x = float(pos.get('x', 100.0))
        place_y = float(pos.get('y', -120.0))
        place_z = float(pos.get('z', 80.0))

        self.get_logger().info(f"🧺 放到车上篮子: "
                               f"({place_x:.0f}, {place_y:.0f}, {place_z:.0f})")

        success = self.arm.place_at(place_x, place_y, place_z,
                                    lift_height=self.car_basket_lift)
        if success:
            self.get_logger().info("  ✅ 已放入篮子")
        else:
            self.get_logger().warn("  ❌ 放入篮子失败")
            # 兜底: 直接松开夹爪
            self.arm.grip(False)

    # ═══════════════════════ 配置加载 ═══════════════════════

    def _load_config(self) -> dict:
        """从参数和默认路径加载配置。"""
        # 先从 ROS2 参数获取配置路径
        config_path = self.declare_parameter(
            'config_file', ''
        ).value

        if not config_path:
            # 尝试在 share 目录找默认配置
            from ament_index_python.packages import get_package_share_directory
            try:
                pkg_dir = get_package_share_directory('fox_grape_harvest')
                default_path = os.path.join(pkg_dir, 'config', 'harvest_config.yaml')
                if os.path.exists(default_path):
                    config_path = default_path
            except Exception:
                pass

        if not config_path:
            # 最后尝试源代码目录
            for candidate in [
                '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml',
                os.path.join(os.path.dirname(__file__), '..', 'config', 'harvest_config.yaml'),
            ]:
                if os.path.exists(candidate):
                    config_path = candidate
                    break

        if not config_path or not os.path.exists(config_path):
            self.get_logger().error(f"❌ 配置文件未找到: {config_path}")
            return {}

        self.get_logger().info(f"📄 加载配置: {config_path}")
        with open(config_path) as f:
            return yaml.safe_load(f)


def _shutdown_cleanup(node, executor) -> None:
    """退出清理：只在 context 还有效时动硬件，每一步都兜异常。

    ⚠️ 为什么必须这么小心（2026-09-21 实测）：
      rclpy 自带的 SIGINT 处理会**在第一次 Ctrl-C 时直接 shutdown context**，
      而 ``Executor.spin()`` 是 ``while context.ok()`` 循环 → 它是「正常返回」而**不是**
      抛 KeyboardInterrupt；等走到这里时 context 已失效，再 publish(/cmd_vel) 或
      调服务(/home) 就会抛::

          RCLError: Failed to publish: publisher's context is invalid

      → 退出时刷一段红色 traceback + ``[ros2run] Process exited with failure 1``，
      现场看着像“程序崩了”（其实只是没法再发指令，硬件已经停了）。
    """
    # 这里全部用 print 而不是 node.get_logger()：日志会往 /rosout 发布，
    # context 失效时同样会抛 RCLError，反而把退出流程再搞脏。
    if rclpy.ok():
        try:
            node.chassis.stop()                 # 底盘急停
        except Exception as exc:
            print(f"[退出] 底盘急停失败（忽略）: {exc}")
        try:
            # 退出时给个短超时：服务没起就等 5s 算了，别把 Ctrl-C 拖成 30~60s 卡顿
            node._arm_home(timeout_sec=5.0)
        except Exception as exc:
            print(f"[退出] 机械臂归位失败（忽略）: {exc}")
    else:
        print("[退出] ROS context 已关闭：跳过底盘急停 / 机械臂归位（Ctrl-C 正常退出）")

    for step, fn in (
        ("executor 关闭", lambda: executor.shutdown(timeout_sec=2.0)),
        ("节点销毁", lambda: node.destroy_node()),
        ("rclpy 关闭", lambda: rclpy.shutdown() if rclpy.ok() else None),
    ):
        try:
            fn()
        except Exception as exc:
            print(f"[退出] {step}异常（忽略）: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = GrapeHarvestNode()
    # ⚠️ 用 MultiThreadedExecutor + 主线程 spin：
    #    采摘流程跑在 worker 线程，主线程必须一直在 spin，否则
    #    /grape_harvest/command（stop/pause）和图像回调都收不到（实测只能收到 1/3）。
    set_external_spin(True)
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:                   # 一般到不了：SIGINT 由 rclpy 内部处理
        print("用户中断")
    finally:
        _shutdown_cleanup(node, executor)


if __name__ == '__main__':
    main()
