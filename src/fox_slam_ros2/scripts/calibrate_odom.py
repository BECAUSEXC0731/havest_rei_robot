#!/usr/bin/env python3
"""
里程计运动模型标定工具
用法：
  平移标定:  ros2 run fox_slam_ros2 calibrate_odom.py --mode linear --dist 2.0
  旋转标定:  ros2 run fox_slam_ros2 calibrate_odom.py --mode angular --angle 360.0
"""

import sys
import math
import time
import argparse
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


def quaternion_to_yaw(q):
    """四元数转偏航角 (弧度), 范围 [-π, π]"""
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class OdomCalibrator(Node):
    def __init__(self, mode, target):
        super().__init__('odom_calibrator')
        self.mode = mode
        self.target = target
        self.start_pose = None
        self.latest_pose = None
        self.prev_yaw = None
        self.total_yaw = 0.0  # 累计旋转角度 (弧度)

        self.sub = self.create_subscription(
            Odometry, '/odom', self.odom_cb, 10)

        self.get_logger().info('=' * 50)
        if mode == 'linear':
            self.get_logger().info(
                f'平移标定: 将机器人直线移动 {target} 米后按 Ctrl+C')
        else:
            self.get_logger().info(
                f'旋转标定: 将机器人原地旋转 {target}° 后按 Ctrl+C')
        self.get_logger().info('=' * 50)

    def odom_cb(self, msg):
        if self.start_pose is None:
            self.start_pose = msg.pose.pose
            if self.mode == 'angular':
                self.prev_yaw = quaternion_to_yaw(msg.pose.pose.orientation)
            return

        self.latest_pose = msg.pose.pose

        # 角度模式：逐帧累积，处理 ±π 环绕
        if self.mode == 'angular':
            cur_yaw = quaternion_to_yaw(msg.pose.pose.orientation)
            delta = cur_yaw - self.prev_yaw
            # 处理环绕：从 +π → -π 是正向跨越
            if delta > math.pi:
                delta -= 2.0 * math.pi
            elif delta < -math.pi:
                delta += 2.0 * math.pi
            self.total_yaw += delta
            self.prev_yaw = cur_yaw

    def compute(self):
        if self.start_pose is None or self.latest_pose is None:
            self.get_logger().error('未收到里程计数据！')
            return

        if self.mode == 'linear':
            start = self.start_pose
            end = self.latest_pose
            dx = end.position.x - start.position.x
            dy = end.position.y - start.position.y
            dist = math.sqrt(dx * dx + dy * dy)
            error = abs(dist - self.target)

            print('\n' + '=' * 50)
            print(f'  目标移动距离:   {self.target:.2f} m')
            print(f'  里程计报告距离: {dist:.4f} m')
            print(f'  绝对误差:       {error:.4f} m')
            print(f'  误差比例:       {dist / self.target:.4f}')
            print(f'  建议 srr ≈ {error / self.target:.4f}')
            print(f'  建议 srt ≈ {error / self.target * 0.5:.4f}')
            print('=' * 50 + '\n')
        else:
            total_deg = math.degrees(abs(self.total_yaw))
            error_deg = abs(total_deg - self.target)

            print('\n' + '=' * 50)
            print(f'  目标旋转角度:   {self.target:.2f}°')
            print(f'  里程计累积旋转: {total_deg:.4f}°')
            print(f'  绝对误差:       {error_deg:.4f}°')
            print(f'  误差比例:       {total_deg / self.target:.4f}')
            print(f'  建议 stt ≈ {error_deg / self.target:.4f}')
            print(f'  建议 str ≈ {error_deg / self.target * 0.5:.4f}')
            print('=' * 50 + '\n')


def main():
    parser = argparse.ArgumentParser(description='里程计运动模型标定')
    parser.add_argument('--mode', choices=['linear', 'angular'],
                        required=True, help='标定模式')
    parser.add_argument('--dist', type=float, default=2.0,
                        help='平移标定的目标距离 (默认: 2.0m)')
    parser.add_argument('--angle', type=float, default=360.0,
                        help='旋转标定的目标角度 (默认: 360°)')
    args = parser.parse_args()

    rclpy.init()
    target = args.dist if args.mode == 'linear' else args.angle
    node = OdomCalibrator(args.mode, target)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.compute()
    node.destroy_node()

    try:
        rclpy.shutdown()
    except Exception:
        pass


if __name__ == '__main__':
    main()
