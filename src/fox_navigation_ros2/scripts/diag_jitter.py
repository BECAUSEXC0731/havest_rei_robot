#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集 6s 的 /cmd_vel /lidar_loc_pose /odom, 判断"原地抖"来源:
   cmd 持续非0(±) → 控制器在下发抖动速度(真抖);
   cmd≈0 但 pose/odom 在±几cm跳 → 定位/显示层抖(假抖)。
用法: python3 diag_jitter.py [sec]"""
import sys, time, math
sys.path.insert(0, '/opt/ros/humble/lib/python3.10/site-packages')
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry


class Jitter(Node):
    def __init__(self, sec):
        super().__init__('diag_jitter')
        self.sec = sec
        self.cmds = []
        self.poses = []
        self.odoms = []
        self.create_subscription(Twist, '/cmd_vel', self.c1, 20)
        self.create_subscription(PoseWithCovarianceStamped, '/lidar_loc_pose', self.c2, 20)
        self.create_subscription(Odometry, '/odom', self.c3, 20)
        self.t0 = time.time()

    def _t(self):
        return round(time.time() - self.t0, 2)

    def c1(self, m):
        self.cmds.append((self._t(), m.linear.x, m.linear.y, m.angular.z))

    def c2(self, m):
        q = m.pose.pose.orientation
        y = math.atan2(2.0*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
        self.poses.append((self._t(), m.pose.pose.position.x, m.pose.pose.position.y, y))

    def c3(self, m):
        q = m.pose.pose.orientation
        y = math.atan2(2.0*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
        self.odoms.append((self._t(), m.pose.pose.position.x, m.pose.pose.position.y, y))

    def run(self):
        end = time.time() + self.sec
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.05)

    @staticmethod
    def stats(name, data, idx):
        if not data:
            print('%-12s 无数据' % name); return
        vals = [d[idx] for d in data]
        lo, hi = min(vals), max(vals)
        nz = sum(1 for v in vals if abs(v) > 1e-4)
        print('%-12s n=%d  range=[%+.4f, %+.4f]  span=%.4f  非零占比=%.0f%%' %
              (name, len(vals), lo, hi, hi - lo, 100.0 * nz / len(vals)))


def main():
    sec = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
    rclpy.init()
    j = Jitter(sec)
    try:
        j.run()
        print('== 抖动统计(采样 %.0fs)===' % sec)
        Jitter.stats('cmd vx', j.cmds, 1)
        Jitter.stats('cmd vy', j.cmds, 2)
        Jitter.stats('cmd vth', j.cmds, 3)
        Jitter.stats('loc x', j.poses, 1)
        Jitter.stats('loc y', j.poses, 2)
        Jitter.stats('loc yaw', j.poses, 3)
        Jitter.stats('odom x', j.odoms, 1)
        Jitter.stats('odom yaw', j.odoms, 3)
        if j.cmds:
            import collections
            c = collections.Counter((round(v[1],3), round(v[2],3), round(v[3],3)) for v in j.cmds)
            print('cmd 常见组合(前5):')
            for k, n in c.most_common(5):
                print('   vx=%+.3f vy=%+.3f vth=%+.3f  x%d' % (k[0], k[1], k[2], n))
    finally:
        j.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
