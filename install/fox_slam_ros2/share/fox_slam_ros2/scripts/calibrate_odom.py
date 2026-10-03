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
    """四元数转偏航角 (弧度)"""
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class OdomCalibrator(Node):
    def __init__(self, mode, target):
        super().__init__('odom_calibrator')
        self.mode = mode
        self.target = target
        self.start_pose = None
        self.result = None

        self.sub = self.create_subscription(
            Odometry, '/odom', self.odom_cb, 10)

        self.get_logger().info('=' * 50)
        if mode == 'linear':
            self.get_logger().info(
                f'平移标定模式：请将机器人移动 {target} 米后按 Ctrl+C')
        else:
            self.get_logger().info(
                f'旋转标定模式：请将机器人旋转 {target}° 后按 Ctrl+C')
        self.get_logger().info('=' * 50)

    def odom_cb(self, msg):
        if self.start_pose is None:
            self.start_pose = msg.pose.pose
            return
        # 持续更新最新位姿
        self.latest_pose = msg.pose.pose

    def compute(self):
        if self.start_pose is None or not hasattr(self, 'latest_pose'):
            self.get_logger().error('未收到里程计数据！')
            return

        start = self.start_pose
        end = self.latest_pose

        if self.mode == 'linear':
            dx = end.position.x - start.position.x
            dy = end.position.y - start.position.y
            dist = math.sqrt(dx * dx + dy * dy)
            error = abs(dist - self.target)
            ratio = dist / self.target

            self.get_logger().info('=' * 50)
            self.get_logger().info(f'目标移动距离: {self.target:.2f} m')
            self.get_logger().info(f'里程计报告距离: {dist:.4f} m')
            self.get_logger().info(f'绝对误差: {error:.4f} m')
            self.get_logger().info(f'误差比例: {ratio:.4f}')
            self.get_logger().info(f'建议 srr ≈ {error / self.target:.4f}')
            self.get_logger().info(f'建议 srt ≈ {error / self.target * 0.5:.4f}')
            self.get_logger().info('=' * 50)
            self.result = error / self.target

        else:  # angular
            yaw_start = quaternion_to_yaw(start.orientation)
            yaw_end = quaternion_to_yaw(end.orientation)
            delta = abs(yaw_end - yaw_start)
            # 处理角度环绕
            if delta > math.pi:
                delta = 2 * math.pi - delta
            delta_deg = math.degrees(delta)
            error_deg = abs(delta_deg - self.target)
            ratio = delta_deg / self.target

            self.get_logger().info('=' * 50)
            self.get_logger().info(f'目标旋转角度: {self.target:.2f}°')
            self.get_logger().info(f'里程计报告角度: {delta_deg:.4f}°')
            self.get_logger().info(f'绝对误差: {error_deg:.4f}°')
            self.get_logger().info(f'误差比例: {ratio:.4f}')
            self.get_logger().info(f'建议 stt ≈ {error_deg / self.target:.4f}')
            self.get_logger().info(f'建议 str ≈ {error_deg / self.target * 0.5:.4f}')
            self.get_logger().info('=' * 50)
            self.result = error_deg / self.target


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
        node.compute()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
