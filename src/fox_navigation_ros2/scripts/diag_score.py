#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 lidar_loc 坐标模型: 在当前 map→odom + odom→base 位姿下, 把最新一帧 /scan
转到 map 系, 分别用 "标准模型" 与 "旧镜像模型" 投影到地图障碍势场上打分。
自洽模型应在 lidar_loc 认为的当前位姿处得到明显高分(贴合墙), 另一模型应低分。

用法(导航运行中, ROS2 终端):
    python3 src/fox_navigation_ros2/scripts/diag_score.py [--sec 6]
判读:
    SCORE std=xxx mirror=xxx    std 明显大 → 新(标准)模型正确, 应贴合
    SCORE std=xxx mirror=xxx    mirror 明显大 → 符号可能还需反转
    MAP/SCAN/TF 缺失 → 导航没在跑或 QoS 不通
"""
import sys, time, math
sys.path.insert(0, '/opt/ros/humble/lib/python3.10/site-packages')
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TransformStamped


def make_gradient(w, h, occupied):
    """同 lidar_loc processMap: 障碍(==100)在 ±50 邻域按 255*(1-d/50) 扩散, 求 max"""
    size = 101
    center = 50
    grad = [[0] * size for _ in range(size)]
    for my in range(size):
        for mx in range(size):
            d = math.hypot(mx - center, my - center)
            grad[my][mx] = int(255.0 * max(0.0, 1.0 - d / center))
    temp = [[0] * w for _ in range(h)]
    for (x, y) in occupied:
        for yy in range(max(0, y - center), min(h - 1, y + center) + 1):
            for xx in range(max(0, x - center), min(w - 1, x + center) + 1):
                v = grad[yy - y + center][xx - x + center]
                if v > temp[yy][xx]:
                    temp[yy][xx] = v
    return temp


class Diag(Node):
    def __init__(self, sec):
        super().__init__('diag_score')
        self.sec = sec
        self.map = None
        self.scan = None
        self.tf = {}   # (parent, child) -> TransformStamped
        q = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                       reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(OccupancyGrid, '/map', self.mcb, q)
        self.create_subscription(LaserScan, '/scan', self.scb, 10)
        self.create_subscription(TransformStamped, '/tf', self.tfb, 10)

    def mcb(self, m): self.map = m
    def scb(self, s): self.scan = s
    def tfb(self, t):
        self.tf[(t.header.frame_id, t.child_frame_id)] = t

    def get_tf(self, parent, child):
        # 简单链式查找(只支持 2 跳内)
        if (parent, child) in self.tf:
            return self.tf[(parent, child)]
        for (p, c), t in self.tf.items():
            if c == child and (parent, p) in self.tf:
                t2 = self.tf[(parent, p)]
                # compose parent<-p<-child
                import copy
                return t2
        return None

    def yaw_of(self, q):
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))

    def run(self):
        t0 = time.time()
        while time.time() - t0 < self.sec:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.map is not None and self.scan is not None:
                break
        if self.map is None or self.scan is None:
            print('NO_DATA map=%s scan=%s' % (self.map is not None, self.scan is not None))
            return
        m = self.map
        res = m.info.resolution
        ox, oy = m.info.origin.position.x, m.info.origin.position.y
        w, h = m.info.width, m.info.height
        occupied = []
        for y in range(h):
            row = m.data[y * w:(y + 1) * w]
            for x, v in enumerate(row):
                if v == 100:
                    occupied.append((x, y))
        print('map %dx%d res=%.3f origin=(%.2f,%.2f) occupied=%d' % (w, h, res, ox, oy, len(occupied)))
        temp = make_gradient(w, h, occupied)

        # base 在 map 的位姿: 用 lidar_loc 发的 map->odom 再乘 odom->base
        mo = self.tf.get(('map', 'odom'))
        ob = self.tf.get(('odom', 'base_footprint'))
        if mo is None or ob is None:
            print('NO_TF map->odom=%s odom->base=%s' % (mo is not None, ob is not None))
            return
        mx, my, myaw = mo.transform.translation.x, mo.transform.translation.y, self.yaw_of(mo.transform.rotation)
        bx, by, byaw = ob.transform.translation.x, ob.transform.translation.y, self.yaw_of(ob.transform.rotation)
        # T_map_base
        yaw = myaw + byaw
        cx, cy = math.cos(yaw), math.sin(yaw)
        rx, ry = mx + cx * bx - cy * by, my + cx * by + cy * bx   # R_map_odom * p_odom_base

        # laser 系 scan 点 (标准 y=+sin); 再转 base 系
        base_laser = self.tf.get(('base_footprint', 'front_lidar_link'))
        lyaw = self.yaw_of(base_laser.transform.rotation)
        lx, ly_ = base_laser.transform.translation.x, base_laser.transform.translation.y
        lc, ls = math.cos(lyaw), math.sin(lyaw)
        pts_std, pts_mir = [], []
        a = self.scan.angle_min
        for rr in self.scan.ranges:
            if rr >= self.scan.range_min and rr <= self.scan.range_max:
                # std laser point (y=+sin); mirror y=-sin
                x0, y0s = rr * math.cos(a), rr * math.sin(a)
                y0m = -y0s
                pts_std.append((lc * x0 - ls * y0s + lx, ls * x0 + lc * y0s + ly_))
                pts_mir.append((lc * x0 - ls * y0m + lx, ls * x0 + lc * y0m + ly_))
            a += self.scan.angle_increment

        def score(pts, sx, sy, syaw):
            c, s = math.cos(syaw), math.sin(syaw)
            tot = 0
            for (px, py_) in pts:
                rxx = c * px - s * py_
                ryy = s * px + c * py_
                col = int((sx + rxx) / res)
                row = int((sy + ryy) / res)
                if 0 <= col < w and 0 <= row < h:
                    tot += temp[row][col]
            return tot

        # 机器人所在 map 栅格(像素)
        gx = (rx - ox) / res
        gy = (ry - oy) / res
        std_s = score(pts_std, rx, ry, yaw)
        mir_s = score(pts_mir, rx, ry, yaw)
        print('base_in_map: x=%.3f y=%.3f yaw=%.1f deg' % (rx, ry, math.degrees(yaw)))
        print('SCORE std=%d mirror=%d  (越大=越贴合墙)' % (std_s, mir_s))
        # 微扰后 std 打分是否在峰(爬山方向)
        s0 = score(pts_std, rx, ry, yaw)
        s1 = score(pts_std, rx + 0.05, ry, yaw)
        s2 = score(pts_std, rx - 0.05, ry, yaw)
        s3 = score(pts_std, rx, ry + 0.05, yaw)
        s4 = score(pts_std, rx, ry - 0.05, yaw)
        print('STD peak check  center=%d +x=%d -x=%d +y=%d -y=%d' % (s0, s1, s2, s3, s4))
        print('=> 若 std 明显大且 center 是峰(local max), 新模型正确; 重启导航后应贴合。')


def main():
    sec = 6
    if len(sys.argv) > 2 and sys.argv[1] == '--sec':
        sec = int(sys.argv[2])
    rclpy.init()
    d = Diag(sec)
    try:
        d.run()
    finally:
        d.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
