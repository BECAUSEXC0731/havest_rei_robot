"""
底盘控制接口
封装对底盘 /cmd_vel 的发送 + Nav2 navigate_to_pose action 调用。
用于：
  1. 导航到固定航点（通过 Nav2）
  2. 微调底盘位置以使葡萄进入机械臂工作空间（闭环里程计反馈）
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

        self.max_vx = 0.3    # m/s
        self.max_vth = 0.5   # rad/s
        self.tolerance = 0.02  # m
        self.adjust_timeout = 15.0  # s

        # 控制参数
        self.kp_angle = 1.5     # 角度 P 控制增益
        self.kp_dist = 1.0      # 距离 P 控制增益
        self.min_vth = 0.1      # 最小旋转速度
        self.min_vx = 0.05      # 最小前进速度
        self.control_rate = 0.05  # 控制周期 50ms (20Hz)

    def set_adjust_params(self, max_vx: float, max_vth: float,
                          tolerance: float, timeout: float):
        """设置微调参数。"""
        self.max_vx = max_vx
        self.max_vth = max_vth
        self.tolerance = tolerance
        self.adjust_timeout = timeout

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
            rclpy.spin_once(self.node, timeout_sec=0.1)
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
        rclpy.spin_until_future_complete(self.node, send_goal_future, timeout_sec=5.0)
        if not send_goal_future.result() or not send_goal_future.result().accepted:
            self.logger.error("导航目标被拒绝")
            return False

        goal_handle = send_goal_future.result()
        self.logger.info("[导航] 目标已接受，等待到达...")

        # 等待结果
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, result_future, timeout_sec=timeout_sec)

        if result_future.result() is None:
            self.logger.warn("[导航] 超时未到达")
            goal_handle.cancel_goal_async()
            return False

        status = result_future.result().status
        if status == 4:  # SUCCEEDED
            self.logger.info("[导航] ✅ 到达目标点")
            return True
        else:
            self.logger.warn(f"[导航] 状态异常: {status}")
            return False

    # ─── 闭环里程计微调 ───

    def adjust_position(self, dx_m: float, dy_m: float) -> bool:
        """
        微调底盘位置（相对当前位姿移动 dx, dy 米）。
        使用里程计反馈进行闭环控制。

        Args:
            dx_m: 前进方向位移（米），正值前进，负值后退
            dy_m: 左右方向位移（米），正值左移，负值右移
        Returns:
            True 表示移动完成
        """
        self.logger.info(f"[底盘微调] 目标移动 (dx={dx_m:.3f}m, dy={dy_m:.3f}m)")

        # 等待里程计数据
        if not self._wait_for_odom():
            self.logger.error("[底盘微调] 无里程计数据，无法闭环控制")
            return False

        # 记录起点
        start_x, start_y, start_yaw = self._get_odom()

        # 目标位置（在起点坐标系下）
        target_x = start_x + dx_m * math.cos(start_yaw) - dy_m * math.sin(start_yaw)
        target_y = start_y + dx_m * math.sin(start_yaw) + dy_m * math.cos(start_yaw)

        self.logger.info(f"[底盘微调] 起点: ({start_x:.3f}, {start_y:.3f}), "
                         f"目标: ({target_x:.3f}, {target_y:.3f})")

        # 闭环控制循环
        start_time = time.time()
        last_log_time = 0.0

        while rclpy.ok():
            elapsed = time.time() - start_time
            if elapsed > self.adjust_timeout:
                self.logger.warn("[底盘微调] ⚠ 超时，停止")
                self.stop()
                return False

            # 获取当前位姿
            cx, cy, cyaw = self._get_odom()
            ex = target_x - cx
            ey = target_y - cy
            dist_error = math.sqrt(ex**2 + ey**2)

            # 每隔 0.5s 打印进度
            if elapsed - last_log_time > 0.5:
                self.logger.info(f"[底盘微调] 剩余距离: {dist_error:.3f}m, "
                                 f"已用时: {elapsed:.1f}s")
                last_log_time = elapsed

            # 到达判定
            if dist_error < self.tolerance:
                self.stop()
                self.logger.info(f"[底盘微调] ✅ 到达目标 (误差 {dist_error*1000:.1f}mm, "
                                 f"耗时 {elapsed:.1f}s)")
                return True

            # 计算期望速度方向（在全局坐标系下指向目标）
            desired_angle = math.atan2(ey, ex)
            angle_error = self._normalize_angle(desired_angle - cyaw)

            # P 控制：距离越远速度越大
            speed = min(self.max_vx, max(self.min_vx, self.kp_dist * dist_error))

            # 如果角度误差较大，先旋转（全向底盘也可以边转边走）
            twist = Twist()
            twist.linear.x = speed * math.cos(angle_error)
            twist.linear.y = speed * math.sin(angle_error)
            twist.angular.z = max(-self.max_vth, min(self.max_vth,
                                  self.kp_angle * angle_error))

            self.cmd_pub.publish(twist)

            # spin 等待下一个控制周期
            rclpy.spin_once(self.node, timeout_sec=self.control_rate)

        return False

    def _rotate_in_place(self, target_heading_rad: float) -> bool:
        """
        原地旋转到目标朝向（闭环控制）。

        Args:
            target_heading_rad: 目标绝对朝向角（弧度）
        Returns:
            True 表示旋转完成
        """
        if not self._wait_for_odom():
            self.logger.error("[旋转] 无里程计数据")
            return False

        angle_tolerance = math.radians(3.0)  # 3° 容差
        start_time = time.time()

        while rclpy.ok():
            elapsed = time.time() - start_time
            if elapsed > 10.0:  # 最多10秒
                self.logger.warn("[旋转] ⚠ 超时")
                self.stop()
                return False

            _, _, cyaw = self._get_odom()
            error = self._normalize_angle(target_heading_rad - cyaw)

            if abs(error) < angle_tolerance:
                self.stop()
                self.logger.info(f"[旋转] ✅ 到位 (误差 {math.degrees(error):.1f}°)")
                return True

            # P 控制
            vth = max(-self.max_vth, min(self.max_vth, self.kp_angle * error))
            if abs(vth) < self.min_vth:
                vth = self.min_vth * (1.0 if error > 0 else -1.0)

            twist = Twist()
            twist.angular.z = vth
            self.cmd_pub.publish(twist)
            rclpy.spin_once(self.node, timeout_sec=0.05)

        return False

    def _drive_forward(self, distance_m: float) -> bool:
        """
        直线前进/后退指定距离（闭环控制）。
        三轮全向底盘：直接沿当前朝向移动。

        Args:
            distance_m: 前进距离（米），正值前进，负值后退
        Returns:
            True 表示移动完成
        """
        if not self._wait_for_odom():
            self.logger.error("[直行] 无里程计数据")
            return False

        # 记录起点
        start_x, start_y, start_yaw = self._get_odom()
        direction = 1.0 if distance_m >= 0 else -1.0
        target_dist = abs(distance_m)

        self.logger.info(f"[直行] 目标: {distance_m:.3f}m, 起点: ({start_x:.3f}, {start_y:.3f})")

        start_time = time.time()

        while rclpy.ok():
            elapsed = time.time() - start_time
            if elapsed > self.adjust_timeout:
                self.logger.warn("[直行] ⚠ 超时")
                self.stop()
                return False

            cx, cy, _ = self._get_odom()
            traveled = math.sqrt((cx - start_x)**2 + (cy - start_y)**2)
            remaining = target_dist - traveled

            if remaining < self.tolerance:
                self.stop()
                self.logger.info(f"[直行] ✅ 到位 (实际 {traveled:.3f}m)")
                return True

            # P 控制
            speed = min(self.max_vx, max(self.min_vx,
                       self.kp_dist * remaining)) * direction
            twist = Twist()
            twist.linear.x = speed
            self.cmd_pub.publish(twist)
            rclpy.spin_once(self.node, timeout_sec=0.05)

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
