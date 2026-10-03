"""
底盘控制接口
封装对底盘 /cmd_vel 的发送 + Nav2 navigate_to_pose action 调用。
用于：
  1. 导航到固定航点（通过 Nav2）
  2. 旋转微调：原地转底盘，把葡萄转到机械臂的理想抓取方向（闭环里程计反馈）

⚠️ 2026-09-22 起**取消平移微调**（原 adjust_position / _drive_forward 已删）：
   旋转改变不了葡萄到机器人的距离 r=hypot(x,y)，只能改方位角；
   所以距离超范围时要靠摆设/人工挪位，不再自动平移。
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from nav2_msgs.action import NavigateToPose
import math
import time
import threading

from fox_grape_harvest.wait_utils import wait_future, pump


class ChassisInterface:
    """底盘控制高层接口。"""

    def __init__(self, node: Node):
        self.node = node
        self.logger = node.get_logger()

        # cmd_vel 发布者（用于微调）
        self.cmd_pub = node.create_publisher(Twist, '/cmd_vel', 1)

        # Nav2 action 客户端（用于导航到航点）
        self.nav_client = ActionClient(node, NavigateToPose, '/navigate_to_pose')

        # ── 里程计订阅（用于闭环微调） ──
        self.odom_x = 0.0
        self.odom_y = 0.0
        self.odom_yaw = 0.0
        self.odom_received = False
        self._odom_lock = threading.Lock()
        self.node.create_subscription(
            Odometry, '/odom', self._odom_callback, 10)

        # ── 旋转微调参数（由 config 的 chassis.rotate_* 注入，见 set_rotate_params）──
        self.rotate_max_vel = 0.5                    # 最大角速度 (rad/s)
        self.rotate_min_vel = 0.1                    # 最小角速度 (rad/s，克服静摩擦)
        self.rotate_kp = 1.5                         # 角度 P 增益
        self.rotate_tolerance = math.radians(3.0)    # 到位容差 (rad)
        self.rotate_timeout = 15.0                   # 单次旋转超时 (s)

        self._active_goal = None    # 当前 Nav2 goal handle（用于停止时取消）
        self.control_rate = 0.05    # 控制周期 50ms (20Hz)

    def set_rotate_params(self, max_vth: float, min_vth: float, kp: float,
                          tolerance_deg: float, timeout: float):
        """注入旋转微调参数（来自 config 的 chassis.rotate_*）。"""
        self.rotate_max_vel = float(max_vth)
        self.rotate_min_vel = float(min_vth)
        self.rotate_kp = float(kp)
        self.rotate_tolerance = math.radians(float(tolerance_deg))
        self.rotate_timeout = float(timeout)

    # ─── 里程计回调 ───

    def _odom_callback(self, msg: Odometry):
        """接收里程计数据，提取 x, y, yaw。"""
        px = msg.pose.pose.position.x
        py = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny, cosy)

        with self._odom_lock:
            self.odom_x = px
            self.odom_y = py
            self.odom_yaw = yaw
            self.odom_received = True

    def _get_odom(self):
        """线程安全地获取里程计数据。"""
        with self._odom_lock:
            return self.odom_x, self.odom_y, self.odom_yaw

    def _wait_for_odom(self, timeout_sec: float = 3.0):
        """等待里程计数据就绪。"""
        waited = 0.0
        while not self.odom_received and waited < timeout_sec:
            pump(self.node, 0.1)
            waited += 0.1
        return self.odom_received

    # ─── Nav2 导航 ───

    def navigate_to(self, x: float, y: float, z: float = 0.0,
                    w: float = 1.0, frame_id: str = "map",
                    timeout_sec: float = 120.0) -> bool:
        """
        通过 Nav2 navigate_to_pose action 导航到目标点。
        Args:
            x, y: 目标位置（map 坐标系，米）
            z, w: 目标朝向四元数
            frame_id: 坐标系
            timeout_sec: 超时秒数
        Returns:
            True 表示导航成功到达
        """
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.logger.error("Nav2 navigate_to_pose action 不可用！请确保 Nav2 已启动")
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = frame_id
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.orientation.z = float(z)
        goal_msg.pose.pose.orientation.w = float(w)

        self.logger.info(f"[导航] 发送目标: ({x:.2f}, {y:.2f})")
        send_goal_future = self.nav_client.send_goal_async(goal_msg)

        # 等待发送完成
        wait_future(self.node, send_goal_future, 5.0)
        if not send_goal_future.result() or not send_goal_future.result().accepted:
            self.logger.error("导航目标被拒绝")
            return False

        goal_handle = send_goal_future.result()
        self.logger.info("[导航] 目标已接受，等待到达...")
        self._active_goal = goal_handle          # 供外部取消/停止

        # 等待结果
        result_future = goal_handle.get_result_async()
        wait_future(self.node, result_future, timeout_sec or 120.0)
        self._active_goal = None

        if not result_future.done() or result_future.result() is None:
            self.logger.warn("[导航] 超时/未到达")
            try:
                goal_handle.cancel_goal_async()
            except Exception:
                pass
            return False

        status = result_future.result().status
        if status == 4:  # SUCCEEDED
            self.logger.info("[导航] ✅ 到达目标点")
            return True
        else:
            self.logger.warn(f"[导航] 状态异常: {status}")
            return False

    # ─── 旋转微调（里程计闭环）───

    def rotate_by(self, delta_rad: float) -> bool:
        """原地旋转一个相对角度（闭环，用 /odom 的 yaw 做反馈）。

        Args:
            delta_rad: 相对当前朝向的旋转量（弧度），**逆时针为正**（ROS 惯例）
        Returns:
            True 表示旋转完成
        """
        if not self._wait_for_odom():
            self.logger.error("[旋转微调] 无里程计数据，无法闭环控制")
            return False

        _, _, start_yaw = self._get_odom()
        target_yaw = self._normalize_angle(start_yaw + float(delta_rad))
        self.logger.info(
            f"[旋转微调] 相对旋转 {math.degrees(delta_rad):+.1f}° "
            f"(yaw {math.degrees(start_yaw):+.1f}° → {math.degrees(target_yaw):+.1f}°), "
            f"容差 {math.degrees(self.rotate_tolerance):.1f}°, "
            f"上限 {self.rotate_max_vel:.2f}rad/s, 超时 {self.rotate_timeout:.0f}s")
        return self._rotate_in_place(target_yaw)

    def _rotate_in_place(self, target_heading_rad: float) -> bool:
        """原地旋转到目标绝对朝向（闭环 P 控制，参数来自 config）。

        Args:
            target_heading_rad: 目标绝对朝向角（odom 系，弧度）
        Returns:
            True 表示旋转到位
        """
        if not self._wait_for_odom():
            self.logger.error("[旋转] 无里程计数据")
            return False

        start_time = time.time()
        last_log_time = 0.0

        while rclpy.ok():
            elapsed = time.time() - start_time
            if elapsed > self.rotate_timeout:
                self.logger.warn(f"[旋转] ⚠ 超时 {elapsed:.1f}s，停止")
                self.stop()
                return False

            _, _, cyaw = self._get_odom()
            error = self._normalize_angle(target_heading_rad - cyaw)

            if elapsed - last_log_time > 0.5:
                self.logger.info(f"[旋转] 剩余 {math.degrees(error):+.1f}°，"
                                 f"已用时 {elapsed:.1f}s")
                last_log_time = elapsed

            if abs(error) < self.rotate_tolerance:
                self.stop()
                self.logger.info(f"[旋转] ✅ 到位 (误差 {math.degrees(error):+.1f}°, "
                                 f"耗时 {elapsed:.1f}s)")
                return True

            # P 控制 + 最小速度（太小会原地不动）
            vth = max(-self.rotate_max_vel,
                      min(self.rotate_max_vel, self.rotate_kp * error))
            if abs(vth) < self.rotate_min_vel:
                vth = self.rotate_min_vel * (1.0 if error > 0 else -1.0)

            twist = Twist()
            twist.angular.z = vth
            self.cmd_pub.publish(twist)
            pump(self.node, self.control_rate)

        return False

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """将角度标准化到 [-π, π]。"""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def stop(self):
        """紧急停止底盘。"""
        self.cmd_pub.publish(Twist())
        self.logger.info("[底盘] 急停")
