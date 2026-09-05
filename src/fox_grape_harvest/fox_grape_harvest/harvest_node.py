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
    --ros-args --params-file config/harvest_config.yaml
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import numpy as np
import yaml
import os
import math
import time
import threading
from collections import deque

from fox_grape_harvest.yolo_detector import YoloDetector
from fox_grape_harvest.depth_utils import (
    load_hand_eye_calibration, depth_to_robot_3d, depth_to_robot_3d_stable,
    load_d2c_config, depth_to_robot_3d_d2c_stable
)
from fox_grape_harvest.arm_interface import ArmInterface
from fox_grape_harvest.chassis_interface import ChassisInterface


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
        self.lift_height = arm_cfg.get('lift_height', 50)
        # 安全裕度（mm），避免刚好在边界上（2026-09-01: 20→10 稍微放宽）
        self.safety_margin = 10

        # ── 导航参数 ──
        nav_cfg = self.config.get('navigation', {})
        self.use_nav2 = nav_cfg.get('use_nav2', True)
        self.nav_timeout = nav_cfg.get('nav_timeout', 120.0)

        # ── 航点配置 ──
        self.waypoints = self.config.get('waypoints', [])
        self.return_to_origin = self.config.get('return_to_origin', True)

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
        self.create_subscription(
            CameraInfo, info_topic, self._info_callback, 1)

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
        self.chassis.set_adjust_params(
            max_vx=chassis_cfg.get('max_linear_vel', 0.3),
            max_vth=chassis_cfg.get('max_angular_vel', 0.5),
            tolerance=chassis_cfg.get('adjust_tolerance', 0.02),
            timeout=chassis_cfg.get('adjust_timeout', 15.0),
        )

        # ── 发布调试可视化 ──
        self.debug_pub = self.create_publisher(Image, '/grape_harvest/debug_image', 1)

        # ── 自动启动（延时等待传感器数据就绪） ──
        self.create_timer(2.0, self._auto_start)

        self.get_logger().info("=" * 60)
        self.get_logger().info("🍇 FOX 葡萄采摘节点已初始化")
        self.get_logger().info(f"   航点数量: {len(self.waypoints)}")
        self.get_logger().info(f"   机械臂工作空间: X[{self.ws_x_min},{self.ws_x_max}] "
                               f"Y[{self.ws_y_min},{self.ws_y_max}] "
                               f"Z[{self.ws_z_min},{self.ws_z_max}]")
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

    # ═══════════════════════ 主流程 ═══════════════════════

    def _auto_start(self):
        """自动启动采摘流程（延迟执行，等待传感器就绪）。"""
        # Humble 的 create_timer 不支持 oneshot 参数，用手动取消实现单次触发
        self._start_timer = self.create_timer(0.0, self._auto_start_once)

    def _auto_start_once(self):
        """定时器回调：取消定时器后执行主流程（只触发一次）。"""
        if self._start_timer is not None:
            self._start_timer.cancel()
        self._run_harvest_workflow()

    def _run_harvest_workflow(self):
        """主采摘工作流。"""
        self.get_logger().info("\n" + "=" * 60)
        self.get_logger().info("🍇 开始葡萄采摘工作流")
        self.get_logger().info("=" * 60)

        if not self.cam_info_received:
            self.get_logger().warn("⏳ 等待相机内参...")
            for _ in range(30):
                rclpy.spin_once(self, timeout_sec=0.5)
                if self.cam_info_received:
                    break
            if not self.cam_info_received:
                self.get_logger().error("❌ 未收到相机内参，终止")
                return

        # 机械臂归位
        self.get_logger().info("🔄 机械臂归位...")
        self.arm.home()

        grape_count = 0

        for i, wp in enumerate(self.waypoints):
            self.get_logger().info(f"\n{'─'*60}")
            self.get_logger().info(f"📍 航点 {i+1}/{len(self.waypoints)}: "
                                   f"{wp.get('description', '')}")
            self.get_logger().info(f"   位置: ({wp['position']['x']:.2f}, {wp['position']['y']:.2f})")
            self.get_logger().info(f"{'─'*60}")

            # 步骤 1: 导航到航点
            if not self._navigate_to_waypoint(wp):
                self.get_logger().warn(f"⚠ 航点 {i+1} 导航失败，跳过")
                continue

            # 步骤 2: 等待图像稳定
            self.get_logger().info("⏳ 等待图像稳定...")
            time.sleep(1.0)
            for _ in range(10):
                rclpy.spin_once(self, timeout_sec=0.1)

            # 步骤 3: 检测 + 抓取（每抓到一颗立即放到车上篮子）
            picked = self._detect_and_pick()
            grape_count += picked

            self.get_logger().info(f"  本航点已摘取 {picked} 颗葡萄")

        # 所有航点已遍历完，没有剩余导航点了 → 返回原点（篮子随车带走）
        if self.return_to_origin:
            self.get_logger().info(f"\n{'─'*60}")
            self.get_logger().info(f"🏠 采摘结束，返回地图原点")
            self.get_logger().info(f"{'─'*60}")
            self._navigate_to_pose(0.0, 0.0, 0.0, 1.0)

        # 机械臂归位
        self.arm.home()

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

    def _detect_and_pick(self) -> int:
        """
        在当前位姿下检测葡萄并逐个抓取。
        Returns:
            已摘取的数量
        """
        if self.detector is None:
            self.get_logger().warn("无 YOLO 检测器，跳过检测")
            return 0

        # 获取最新 RGB-D 帧
        rgb, depth = self._get_synced_frames()
        if rgb is None or depth is None:
            self.get_logger().warn("未获取到图像帧")
            return 0

        # YOLO 检测
        detections = self.detector.detect(rgb)
        self.get_logger().info(f"🔍 YOLO 检测到 {len(detections)} 个目标")

        if len(detections) == 0:
            return 0

        # 发布调试图像
        debug_img = self.detector.draw_detections(rgb, detections)
        self._publish_debug_image(debug_img)

        picked = 0
        for idx, det in enumerate(detections):
            self.get_logger().info(f"\n  ── 目标 {idx+1}/{len(detections)} ──")
            cx, cy = det['center']

            # 获取 3D 位置（机器人坐标系，毫米）——跨帧取中值抗深度闪烁
            with self._img_lock:
                frames = [f.copy() for f in self.depth_history] or [depth]
            if self.T_color_to_ir is not None:
                pt_robot_mm, depth_m = depth_to_robot_3d_d2c_stable(
                    cx, cy, frames, self.camera_matrix, self.K_ir,
                    self.T_color_to_ir, self.T_cam_to_robot)
            else:
                pt_robot_mm, depth_m = depth_to_robot_3d_stable(
                    cx, cy, frames, self.camera_matrix, self.T_cam_to_robot)
            if pt_robot_mm is None:
                self.get_logger().warn(f"  深度无效 (像素 {cx},{cy})，跳过")
                continue

            rx, ry, rz = pt_robot_mm
            self.get_logger().info(f"  葡萄位置 (机器人坐标系): "
                                   f"({rx:.0f}, {ry:.0f}, {rz:.0f}) mm")

            # 检查是否在机械臂工作空间内
            reachable = self._is_reachable(rx, ry, rz)

            if reachable:
                self.get_logger().info(f"  ✅ 机械臂可直接到达")
            else:
                self.get_logger().info(f"  ⚠ 超出机械臂工作空间，需移动底盘")
                if not self._adjust_chassis_for_grape(rx, ry):
                    self.get_logger().error("  ❌ 无法调整底盘到达葡萄位置")
                    continue
                # 移动后重新检测
                self.get_logger().info("  移动后重新检测...")
                time.sleep(1.0)
                # 重新获取帧并检测
                rgb2, depth2 = self._get_synced_frames()
                if rgb2 is None:
                    continue
                detections2 = self.detector.detect(rgb2)
                if not detections2:
                    self.get_logger().warn("  重检测未找到葡萄")
                    continue
                # 取最近的目标
                det2 = detections2[0]
                cx2, cy2 = det2['center']
                with self._img_lock:
                    frames2 = [f.copy() for f in self.depth_history] or [depth2]
                if self.T_color_to_ir is not None:
                    pt2, _ = depth_to_robot_3d_d2c_stable(
                        cx2, cy2, frames2, self.camera_matrix, self.K_ir,
                        self.T_color_to_ir, self.T_cam_to_robot)
                else:
                    pt2, _ = depth_to_robot_3d_stable(
                        cx2, cy2, frames2, self.camera_matrix, self.T_cam_to_robot)
                if pt2 is None:
                    continue
                rx, ry, rz = pt2
                self.get_logger().info(f"  重检测位置: ({rx:.0f}, {ry:.0f}, {rz:.0f}) mm")
                if not self._is_reachable(rx, ry, rz):
                    self.get_logger().warn("  调整后仍不可达，跳过")
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

    def _is_reachable(self, x_mm: float, y_mm: float, z_mm: float) -> bool:
        """
        判断目标点是否在机械臂工作空间内（含安全裕度）。
        Args:
            x_mm, y_mm, z_mm: 机器人坐标系下的坐标（毫米）
        Returns:
            True 表示可达
        """
        margin = self.safety_margin
        in_x = (self.ws_x_min + margin) <= x_mm <= (self.ws_x_max - margin)
        in_y = (self.ws_y_min + margin) <= y_mm <= (self.ws_y_max - margin)
        in_z = (self.ws_z_min + margin) <= z_mm <= (self.ws_z_max - margin)
        return in_x and in_y and in_z

    def _adjust_chassis_for_grape(self, grape_x_mm: float, grape_y_mm: float) -> bool:
        """
        计算并执行底盘微调，使葡萄进入机械臂工作空间。
        目标: 使葡萄位置接近机械臂的理想抓取中心 (preferred_x, preferred_y)。

        因为机械臂在底盘中心正上方，所以:
        - 如果 grape_x_mm > ws_x_max → 底盘需要前进 (dx > 0)
        - 如果 grape_x_mm < ws_x_min → 底盘需要后退 (dx < 0)
        - 如果 grape_y_mm > ws_y_max → 底盘需要左移 (dy > 0)
        - 如果 grape_y_mm < ws_y_min → 底盘需要右移 (dy < 0)

        移动量 = 葡萄位置 - 理想抓取中心（并转换到米）
        """
        dx_m = (grape_x_mm - self.preferred_x) / 1000.0
        dy_m = (grape_y_mm - self.preferred_y) / 1000.0

        self.get_logger().info(f"  底盘调整量: dx={dx_m:.3f}m, dy={dy_m:.3f}m")
        return self.chassis.adjust_position(dx_m, dy_m)

    # ═══════════════════════ 抓取/放置执行 ═══════════════════════

    def _pick_grape(self, x_mm: float, y_mm: float, z_mm: float) -> bool:
        """
        在目标位置执行葡萄抓取（夹爪）。
        流程:
          1. 移动到安全高度上方
          2. 下降到葡萄位置 + 夹爪夹紧
          3. 抬升（保持夹住）
        """
        self.get_logger().info(f"\n  🦾 抓取葡萄: ({x_mm:.0f}, {y_mm:.0f}, {z_mm:.0f})")

        # 如果 z 太小（贴地），提升到安全高度
        pick_z = max(z_mm, 30.0)

        success = self.arm.pick_at(x_mm, y_mm, pick_z, lift_height=self.lift_height)
        if success:
            self.get_logger().info("  ✅ 抓取成功！")
        else:
            self.get_logger().warn("  ❌ 抓取失败")
        return success

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


def main(args=None):
    rclpy.init(args=args)
    node = GrapeHarvestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("用户中断")
    finally:
        # 停止底盘
        if hasattr(node, 'chassis'):
            node.chassis.stop()
        # 机械臂归位
        if hasattr(node, 'arm'):
            node.arm.home()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
