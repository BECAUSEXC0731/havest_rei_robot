#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断 lidar_loc: 采集 /map /initialpose /lidar_loc_pose 12 秒, 判断位姿跳走原因"""
import sys, os, time, math
sys.path.insert(0, '/opt/ros/humble/lib/python3.10/site-packages')
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseWithCovarianceStamped


class Diag(Node):
    def __init__(self):
        super().__init__('diag_loc')
        self.map_cnt = 0
        self.map_t = []
        self.map_wh = None
        self.map_origin = None
        self.map_res = None
        self.poses = []
        self.inits = []
        self.create_subscription(OccupancyGrid, '/map', self.mcb, 10)
        self.create_subscription(PoseWithCovarianceStamped, '/lidar_loc_pose', self.pcb, 10)
        self.create_subscription(PoseWithCovarianceStamped, '/initialpose', self.icb, 10)
        self.t0 = time.time()

    def mcb(self, m):
        if self.map_wh is None:
            self.map_wh = (m.info.width, m.info.height)
            self.map_origin = (m.info.origin.position.x, m.info.origin.position.y)
            self.map_res = m.info.resolution
        self.map_cnt += 1
        self.map_t.append(round(time.time() - self.t0, 2))

    def pcb(self, p):
        x = p.pose.pose.position.x
        y = p.pose.pose.position.y
        q = p.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.poses.append((round(time.time() - self.t0, 2), round(x, 3), round(y, 3),
                           round(math.degrees(yaw), 1)))

    def icb(self, p):
        q = p.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.inits.append((round(time.time() - self.t0, 2),
                           round(p.pose.pose.position.x, 3),
                           round(p.pose.pose.position.y, 3),
                           round(math.degrees(yaw), 1)))


rclpy.init()
n = Diag()
print('diag started; sampling 12s...')
end = time.time() + 12
while time.time() < end:
    rclpy.spin_once(n, timeout_sec=0.1)
n.destroy_node()
rclpy.shutdown()
print('map count:', n.map_cnt, 'map times:', n.map_t[:10])
print('map w,h:', n.map_wh, 'origin:', n.map_origin, 'res:', n.map_res)
print('initialpose events:', n.inits)
print('lidar_loc_pose samples (%d):' % len(n.poses))
for r in n.poses[:50]:
    print('  t=%s x=%s y=%s yaw=%s' % r)
if len(n.poses) > 50:
    print('  ... total', len(n.poses))
