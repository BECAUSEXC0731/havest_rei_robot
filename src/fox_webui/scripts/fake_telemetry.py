#!/usr/bin/env python3
"""fake_telemetry.py — 无硬件时给 WebUI 灌假数据（开发/演示/回归用）。

解决的问题
----------
现场机器人不在手边（或底盘/机械臂没上电）时，WebUI 只能显示空值，无法验证
"话题 → StateStore → SSE → 页面"这条链路。本脚本按真实话题名与类型发布可预期的
数值，于是任何一项显示不对都能立刻定位是前端/后端的问题，而不是硬件没插。

发布的话题（与真实驱动一致）
--------------------------
  /odom                          nav_msgs/Odometry              10Hz  vx=0.15 vy=0.02 vth=0.30
  /cmd_vel                       geometry_msgs/Twist             1Hz
  /car_data                      rei_robot_base/CarData          5Hz  电压 24.5V 充电中
  /arm_controller/position_info  arm_controller/Control         10Hz  (200,10,130) mm
  /gripper/state                 std_msgs/Int32                  2Hz  脉宽可指定
  /lidar_loc_pose                geometry_msgs/PoseWithCovarianceStamped 10Hz (1.0, 2.0) m
  /rosout                        由节点日志自动产生（用于验证日志面板）

用法
----
    source scripts/fox_webui_env.sh
    python3 scripts/fake_telemetry.py                      # 一直发，Ctrl+C 结束
    python3 scripts/fake_telemetry.py --duration 30        # 发 30 秒后自动退出
    python3 scripts/fake_telemetry.py --gripper-pulse 500  # 模拟"松开"
"""
from __future__ import annotations

import argparse
import math
import time

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from std_msgs.msg import Int32
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped, PoseStamped
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import CameraInfo, Image, LaserScan

from arm_controller.msg import Control
from arm_controller.srv import Move, RelativePos
from rei_robot_base.msg import CarData

# 彩色内参默认值（与 calib_data/color/color_camera_info.yaml 一致）
DEFAULT_K = (607.4669, 603.8284, 323.4215, 245.5242)


class FakeTelemetry(Node):

    def __init__(self, gripper_pulse: int, voltage: float, arm_xyz,
                 with_camera: bool = False, with_scan: bool = False,
                 with_services: bool = False, echo_cmd_vel: bool = False):
        super().__init__('fake_telemetry')
        self.gripper_pulse = gripper_pulse
        self.voltage = voltage
        self.arm_xyz = arm_xyz
        self.with_camera = with_camera
        self.with_scan = with_scan
        self.with_services = with_services
        self.t0 = time.time()
        self._last_cmd = None
        self.fx, self.fy, self.cx, self.cy = DEFAULT_K
        # 合成"葡萄"在图像中的位置/半径（像素）
        self.grape_u, self.grape_v, self.grape_r = 320, 240, 45

        self.pub_odom = self.create_publisher(Odometry, '/odom', 10)
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_car = self.create_publisher(CarData, '/car_data', 10)
        self.pub_arm = self.create_publisher(Control, '/arm_controller/position_info', 10)
        self.pub_grip = self.create_publisher(Int32, '/gripper/state', 10)
        self.pub_pose = self.create_publisher(PoseWithCovarianceStamped, '/lidar_loc_pose', 10)

        if self.with_camera:
            self.pub_rgb = self.create_publisher(Image, '/camera/color/image_raw', 10)
            self.pub_depth = self.create_publisher(Image, '/camera/depth/image_raw', 10)
            self.pub_info = self.create_publisher(
                CameraInfo, '/camera/color/camera_info', qos_profile_sensor_data)
        if self.with_scan:
            self.pub_scan = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data)
            self.pub_path = self.create_publisher(Path, '/plan', 10)

        # ── 假服务：让 WebUI 的控制按钮在无硬件时也能走通 ──
        #    goto_position 会直接改写 arm_xyz，下一次 10Hz 发布就带着新位置出去，
        #    → 界面上“机械臂位置”会跟着动 = 端到端可见；夹爪同理会改脉宽。
        if self.with_services:
            self.create_service(Move, 'goto_position', self._on_goto)
            self.create_service(RelativePos, 'relative_position', self._on_relative)
            self.create_service(SetBool, 'home', self._on_home)
            self.create_service(SetBool, 'unlock', self._on_ack)
            self.create_service(SetBool, 'set_zero', self._on_ack)
            self.create_service(SetBool, 'gripper/grip', self._on_grip)

        # ── 回显 /cmd_vel：验证手动控制/看门狗/急停是否真的发出去了 ──
        if echo_cmd_vel:
            self.create_subscription(Twist, '/cmd_vel', self._on_cmd_vel, 10)

        self.create_timer(0.1, self._tick_10hz)     # odom / arm / pose / scan
        self.create_timer(0.2, self._tick_5hz)      # car_data
        self.create_timer(0.5, self._tick_2hz)      # gripper
        self.create_timer(1.0, self._tick_1hz)      # cmd_vel / plan
        self.create_timer(5.0, self._tick_5s)       # 日志（验证 /rosout 面板）
        if self.with_camera:
            # 彩色与深度各自独立定时器：一次回调里同时发两张图（1.5MB）
            # 会把实际频率拖到 3Hz 左右，测不出 10fps 视频（实测踩过）
            self.create_timer(0.1, self._pub_color)
            self.create_timer(0.11, self._pub_depth)
            self.create_timer(1.0, self._pub_info)

        self.get_logger().info(
            f'fake_telemetry 已启动: 电压={voltage}V 夹爪脉宽={gripper_pulse} '
            f'机械臂={arm_xyz} camera={with_camera} scan={with_scan} services={with_services}')

    # ══════════ 假服务回调 ══════════

    def _on_goto(self, req, res):
        p = req.pose.position
        self.arm_xyz = (p.x, p.y, p.z)
        self.get_logger().info(
            f'[fake-arm] goto_position -> ({p.x:.0f}, {p.y:.0f}, {p.z:.0f}) '
            f'roll={math.degrees(req.pose.roll):.0f}°')
        res.success = True
        res.message = 'fake arm ok'
        return res

    def _on_relative(self, req, res):
        x, y, z = self.arm_xyz
        self.arm_xyz = (x + req.dx, y + req.dy, z + req.dz)
        self.get_logger().info(
            f'[fake-arm] relative_position -> ({self.arm_xyz[0]:.0f}, '
            f'{self.arm_xyz[1]:.0f}, {self.arm_xyz[2]:.0f})')
        res.success = True
        res.message = 'fake relative ok'
        return res

    def _on_home(self, req, res):
        self.arm_xyz = (200.0, 0.0, 150.0)
        self.get_logger().info('[fake-arm] home -> (200, 0, 150)')
        res.success = True
        res.message = 'fake home ok'
        return res

    def _on_ack(self, req, res):
        self.get_logger().info(f'[fake-arm] 服务被调用: {getattr(req, "data", None)}')
        res.success = True
        res.message = 'fake ack'
        return res

    def _on_grip(self, req, res):
        self.gripper_pulse = 2000 if req.data else 500
        self.get_logger().info(
            f'[fake-gripper] grip close={req.data} -> pulse={self.gripper_pulse}')
        res.success = True
        res.message = f'pulse={self.gripper_pulse}'
        return res

    def _on_cmd_vel(self, msg):
        v = (round(msg.linear.x, 3), round(msg.linear.y, 3), round(msg.angular.z, 3))
        if v != self._last_cmd:
            self._last_cmd = v
            self.get_logger().info(
                f'[fake-base] 收到 /cmd_vel: vx={v[0]} vy={v[1]} vth={v[2]}')

    # ── 10Hz ──
    def _tick_10hz(self):
        t = time.time() - self.t0

        o = Odometry()
        o.header.stamp = self.get_clock().now().to_msg()
        o.header.frame_id = 'odom'
        o.child_frame_id = 'base_footprint'
        o.pose.pose.position.x = 1.0
        o.pose.pose.position.y = 2.0
        o.pose.pose.orientation.w = 1.0
        o.twist.twist.linear.x = 0.15
        o.twist.twist.linear.y = 0.02
        o.twist.twist.angular.z = 0.30
        self.pub_odom.publish(o)

        a = Control()
        a.position.x = float(self.arm_xyz[0])
        a.position.y = float(self.arm_xyz[1]) + 3.0 * math.sin(t)      # 轻微摆动，便于看"实时"
        a.position.z = float(self.arm_xyz[2])
        a.roll, a.pitch, a.yaw = 0.0, 0.0, 0.0
        self.pub_arm.publish(a)

        p = PoseWithCovarianceStamped()
        p.header.stamp = self.get_clock().now().to_msg()
        p.header.frame_id = 'map'
        p.pose.pose.position.x = 1.0
        p.pose.pose.position.y = 2.0
        p.pose.pose.orientation.w = 1.0
        self.pub_pose.publish(p)

        if self.with_camera:
            self._pub_color()
            self._pub_depth()
            self._pub_info()
        if self.with_scan:
            self._pub_scan()

    # ── 合成相机（彩色 / 深度 / 内参 各自独立发布）──
    def _grape_mask(self):
        h, w = 480, 640
        yy, xx = np.mgrid[0:h, 0:w]
        return (xx - self.grape_u) ** 2 + (yy - self.grape_v) ** 2 <= self.grape_r ** 2

    def _pub_color(self):
        """造一张带"葡萄"的彩色图（BGR）。"""
        h, w = 480, 640
        img = np.full((h, w, 3), 45, np.uint8)
        img[:, :, 0] = np.linspace(30, 70, w, dtype=np.uint8)[None, :]   # B 渐变
        img[:, :, 1] = 50
        img[self._grape_mask()] = (60, 180, 70)                          # 绿葡萄(BGR)

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_color_optical_frame'
        msg.height, msg.width = h, w
        msg.encoding = 'bgr8'
        msg.is_bigendian = 0
        msg.step = w * 3
        msg.data = img.tobytes()
        self.pub_rgb.publish(msg)

    def _pub_depth(self):
        """深度图，单位 **厘米**（16UC1）—— 与真机一致，后端 /100 转米。"""
        h, w = 480, 640
        depth = np.full((h, w), 200, np.uint16)     # 背景 200cm = 2.00m
        depth[self._grape_mask()] = 60              # 葡萄前表面 60cm = 0.60m
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_depth_optical_frame'
        msg.height, msg.width = h, w
        msg.encoding = '16UC1'
        msg.is_bigendian = 0
        msg.step = w * 2
        msg.data = depth.tobytes()
        self.pub_depth.publish(msg)

    def _pub_info(self):
        h, w = 480, 640
        info = CameraInfo()
        info.header.stamp = self.get_clock().now().to_msg()
        info.header.frame_id = 'camera_color_optical_frame'
        info.height, info.width = h, w
        info.distortion_model = 'plumb_bob'
        info.d = [0.0] * 5
        info.k = [self.fx, 0.0, self.cx, 0.0, self.fy, self.cy, 0.0, 0.0, 1.0]
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        info.p = [self.fx, 0.0, self.cx, 0.0, 0.0, self.fy, self.cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        self.pub_info.publish(info)

    # ── 合成激光（机器人周围一圈"墙"）──
    def _pub_scan(self):
        n = 360
        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = 'front_lidar_link'
        scan.angle_min = -math.pi
        scan.angle_max = math.pi
        scan.angle_increment = 2 * math.pi / n
        scan.range_min = 0.1
        scan.range_max = 8.0
        scan.ranges = [1.2 + 0.3 * math.sin(3 * (-math.pi + i * 2 * math.pi / n))
                       for i in range(n)]
        self.pub_scan.publish(scan)

    # ── 5Hz ──
    def _tick_5hz(self):
        c = CarData()
        c.header.stamp = self.get_clock().now().to_msg()
        c.motor_speed = [12.0, 11.5, 12.2]
        c.crash = [0, 0]
        c.cliff = [0, 0]
        c.ultrasound = [0.5, 0.6]
        c.smoke = 0
        c.power_voltage = float(self.voltage)
        c.is_charge = True
        self.pub_car.publish(c)

    # ── 2Hz ──
    def _tick_2hz(self):
        g = Int32()
        g.data = int(self.gripper_pulse)
        self.pub_grip.publish(g)

    # ── 1Hz ──
    def _tick_1hz(self):
        v = Twist()
        v.linear.x = 0.0
        v.linear.y = 0.0
        v.angular.z = 0.0
        self.pub_cmd.publish(v)
        if self.with_scan:
            self._pub_path()

    # ── 合成全局路径（地图上的一条绿线）──
    def _pub_path(self):
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'map'
        for i in range(25):
            ps = PoseStamped()
            ps.header = path.header
            ps.pose.position.x = 1.0 + i * 0.08
            ps.pose.position.y = 2.0 + i * 0.03
            ps.pose.orientation.w = 1.0
            path.poses.append(ps)
        self.pub_path.publish(path)

    # ── 5s ──
    def _tick_5s(self):
        self.get_logger().info('fake_telemetry: 心跳（这条日志用于验证 /rosout 面板）')


def main():
    ap = argparse.ArgumentParser(description='给 WebUI 灌假数据（无硬件测试）')
    ap.add_argument('--gripper-pulse', type=int, default=2000,
                    help='夹爪脉宽 2000=抓紧 / 500=松开')
    ap.add_argument('--voltage', type=float, default=24.5)
    ap.add_argument('--duration', type=float, default=0.0, help='发布时长(秒)，0=一直发')
    ap.add_argument('--camera', action='store_true',
                    help='同时发布合成彩色/深度/内参（验证视频与识别）')
    ap.add_argument('--scan', action='store_true',
                    help='同时发布合成 /scan 与 /plan（验证地图视图）')
    ap.add_argument('--fake-services', action='store_true',
                    help='同时提供假的 goto_position/home/gripper 等服务（验证控制链路）')
    ap.add_argument('--echo-cmd-vel', action='store_true',
                    help='回显收到的 /cmd_vel（验证手动控制/看门狗/急停）')
    ap.add_argument('--all', action='store_true',
                    help='等价于 --camera --scan --fake-services --echo-cmd-vel')
    args = ap.parse_args()

    rclpy.init()
    node = FakeTelemetry(args.gripper_pulse, args.voltage, (200.0, 10.0, 130.0),
                         with_camera=args.camera or args.all,
                         with_scan=args.scan or args.all,
                         with_services=args.fake_services or args.all,
                         echo_cmd_vel=args.echo_cmd_vel or args.all)
    try:
        if args.duration > 0:
            end = time.time() + args.duration
            while rclpy.ok() and time.time() < end:
                rclpy.spin_once(node, timeout_sec=0.1)
        else:
            rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
