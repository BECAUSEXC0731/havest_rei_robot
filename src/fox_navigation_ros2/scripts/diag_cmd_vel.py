#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航方向诊断工具：同时监听 /cmd_vel、/odom、/lidar_loc_pose(lidar_loc 定位)，
定位“物理左移但 RViz 里相对地图反向”等问题。

用法（导航运行中，已 source ROS）：
    python3 src/fox_navigation_ros2/scripts/diag_cmd_vel.py

手动让机器人前进/左移/原地左转各 2 秒，观察每 1 秒打印一行。判读：
    CMD   vx>0 表示“控制器想前进”（机器人 base 系）
    ODOM  pos.y 增大  表示底盘里程计记录的是“前进”（正确）
    LOC   yaw 接近 0° 表示定位认为机器人朝前（地图系）

    若 ODOM 前进方向与 CMD 一致、但 LOC 的 pos/yaw 变化方向相反
        → odom 正确，问题在定位/map 层（初始位姿给反 180°/对称环境锁反）
    若 ODOM 本身与 CMD 相反（物理前进但 odom 后退）
        → 问题在底盘里程计方向（运动学/电机反馈符号）
"""
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
from nav_msgs.msg import Odometry


class DiagNode(Node):
    def __init__(self):
        super().__init__('diag_cmd_vel')
        self.last_cmd = None
        self.last_odom = None
        self.last_loc = None
        # 订阅控制器下发的速度
        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        # 订阅底盘里程计（实际运动）
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        # 订阅 lidar_loc 定位估计（map 系位姿）
        self.create_subscription(
            PoseWithCovarianceStamped, '/lidar_loc_pose', self.loc_cb, 10)
        # 每 1 秒打印一次
        self.create_timer(1.0, self.print_status)

    def cmd_cb(self, msg):
        self.last_cmd = msg

    def odom_cb(self, msg):
        self.last_odom = msg

    def loc_cb(self, msg):
        self.last_loc = msg

    @staticmethod
    def _yaw(q):
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                          1.0 - 2.0 * (q.y * q.y + q.z * q.z))

    def print_status(self):
        parts = []
        # —— 控制器在发什么 ——
        if self.last_cmd is not None:
            c = self.last_cmd
            parts.append(
                f"CMD vx={c.linear.x:+.3f} vy={c.linear.y:+.3f} vth={c.angular.z:+.3f}")
        else:
            parts.append("CMD <无 /cmd_vel 数据(目标没到控制器?)>")
        # —— 机器人实际动没动（odom 系）——
        if self.last_odom is not None:
            o = self.last_odom
            p = o.pose.pose.position
            yaw = self._yaw(o.pose.pose.orientation)
            t = o.twist.twist
            parts.append(
                f"ODOM vx={t.linear.x:+.3f} vy={t.linear.y:+.3f} vth={t.angular.z:+.3f} "
                f"pos=({p.x:+.3f},{p.y:+.3f}) yaw={math.degrees(yaw):+.1f}")
        else:
            parts.append("ODOM <无 /odom 数据>")
        # —— lidar_loc 定位（map 系）——
        if self.last_loc is not None:
            p = self.last_loc.pose.pose.position
            yaw = self._yaw(self.last_loc.pose.pose.orientation)
            parts.append(
                f"LOC pos=({p.x:+.3f},{p.y:+.3f}) yaw={math.degrees(yaw):+.1f}")
        else:
            parts.append("LOC <无 /lidar_loc_pose 数据(lidar_loc 没在跑?)>")
        self.get_logger().info(" | ".join(parts))


def main(args=None):
    rclpy.init(args=args)
    node = DiagNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
