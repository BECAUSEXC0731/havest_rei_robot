#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 /local_costmap/costmap(含膨胀) 与 costmap_raw(未膨胀) 里高代价格子的分布，
量出"围住车的红圈"距离车多远、多宽、是不是一圈。

用法（导航运行中，已 source ROS 的终端）：
    python3 src/fox_navigation_ros2/scripts/diag_costmap.py

输出例：
  [costmap   ] 高代价格=412(其中>=90的=88) | 距车距离带(0.1m/格): 0.4m:9 0.5m:56 0.6m:120 0.7m:140 ...
  [costmap_raw] 高代价格=96 | 距车距离带: 0.4m:9 0.5m:56 ... 
判读：
  - 若 costmap_raw 里距离车 0.x m 就有障碍格 → 那圈是激光真的扫到的东西(车身/真实障碍)
  - 若 costmap_raw 车附近干净、只有 costmap(含膨胀)有圈 → 圈是膨胀造成的
  - 距离带如果只集中在某一段(如 0.5~0.7m)且一圈都有 → 固定半径的包围圈
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid


class DiagCostmap(Node):
    def __init__(self):
        super().__init__('diag_costmap')
        self.costmap = None
        self.raw = None
        self.create_subscription(OccupancyGrid, '/local_costmap/costmap', self.cb_costmap, 10)
        self.create_subscription(OccupancyGrid, '/local_costmap/costmap_raw', self.cb_raw, 10)
        self.create_timer(2.0, self.report)

    def cb_costmap(self, msg):
        self.costmap = msg

    def cb_raw(self, msg):
        self.raw = msg

    @staticmethod
    def bands(msg):
        """返回 {距离带: 高代价格数}，以滚动窗口中心为车的位置。"""
        w, h = msg.info.width, msg.info.height
        res = msg.info.resolution
        cx, cy = w / 2.0, h / 2.0
        out = {}
        lethal = 0
        for y in range(h):
            for x in range(w):
                v = msg.data[y * w + x]
                if v < 50:
                    continue
                dx = (x - cx) * res
                dy = (y - cy) * res
                d = (dx * dx + dy * dy) ** 0.5
                if v >= 90:
                    lethal += 1
                b = round(d * 10) / 10.0
                out[b] = out.get(b, 0) + 1
        return out, lethal

    def report(self):
        if self.costmap is None:
            self.get_logger().info('等待 /local_costmap/costmap ...')
            return
        b, lethal = self.bands(self.costmap)
        parts = [f"{k:.1f}m:{v}" for k, v in sorted(b.items())][:16]
        self.get_logger().info(
            f"[costmap   ] 高代价格={sum(b.values())}(>=90:{lethal}) | 距车: "
            + (", ".join(parts) if parts else "无"))
        if self.raw is not None:
            rb, rlethal = self.bands(self.raw)
            rparts = [f"{k:.1f}m:{v}" for k, v in sorted(rb.items())][:16]
            self.get_logger().info(
                f"[costmap_raw] 高代价格={sum(rb.values())}(>=90:{rlethal}) | 距车: "
                + (", ".join(rparts) if rparts else "无"))


def main():
    rclpy.init()
    n = DiagCostmap()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    finally:
        n.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
