#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航话题诊断：检查规划/控制相关话题是否在发布、数据长什么样。

用法（已 source ROS 的终端里，导航运行中）：
    python3 src/fox_navigation_ros2/scripts/diag_nav_topics.py

然后给一个导航目标，观察每 1 秒打印一行，例如：
    GlobalPlan=点:23 | LocalPlan=<无数据> | GlobalCostmap=238x245 障碍:... | LocalCostmap=... | CMD vx=... | ODOM pos=(...)

判断：
    - GlobalPlan 有数据(绿线) 但 LocalPlan 无数据(无蓝线)  → 控制器没在跟随/没输出局部路径
    - LocalCostmap 无数据  → 局部代价地图没在发布（查 controller_server / TF）
    - LocalCostmap 有数据但"障碍:0 膨胀:0"全是免费  → 激光没进局部代价地图（查 /scan 话题、TF）
    - CMD vx 非零 但 ODOM pos 不动  → 底盘没执行（底盘/电机问题）
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path, Odometry
from geometry_msgs.msg import Twist


class DiagNavTopics(Node):
    def __init__(self):
        super().__init__('diag_nav_topics')
        # 话题 -> 消息类型
        self.subs = {
            '/plan': Path,
            '/local_plan': Path,
            '/global_costmap/costmap': OccupancyGrid,
            '/local_costmap/costmap': OccupancyGrid,
            '/cmd_vel': Twist,
            '/odom': Odometry,
        }
        self.last = {}
        self.count = {}
        for topic, msg_type in self.subs.items():
            self.last[topic] = None
            self.count[topic] = 0
            self.create_subscription(msg_type, topic, self._make_cb(topic), 10)
        self.create_timer(1.0, self.print_status)

    def _make_cb(self, topic):
        def cb(msg):
            self.last[topic] = msg
            self.count[topic] += 1
        return cb

    def print_status(self):
        parts = []
        for topic in ['/plan', '/local_plan', '/global_costmap/costmap',
                      '/local_costmap/costmap', '/cmd_vel', '/odom']:
            msg = self.last.get(topic)
            if msg is None:
                parts.append(f"{topic}=<无数据>")
                continue
            if isinstance(msg, Path):
                parts.append(f"{topic}=点:{len(msg.poses)}")
            elif isinstance(msg, OccupancyGrid):
                data = msg.data
                lethal = sum(1 for c in data if c >= 99)
                infl = sum(1 for c in data if 0 < c < 99)
                unknown = sum(1 for c in data if c < 0)
                free = sum(1 for c in data if c == 0)
                parts.append(
                    f"{topic}=WxH:{msg.info.width}x{msg.info.height} "
                    f"自由:{free} 障碍:{lethal} 膨胀:{infl} 未知:{unknown}")
            elif isinstance(msg, Twist):
                c = msg
                parts.append(
                    f"{topic}=vx:{c.linear.x:+.3f} vy:{c.linear.y:+.3f} vth:{c.angular.z:+.3f}")
            elif isinstance(msg, Odometry):
                p = msg.pose.pose.position
                yaw = msg.pose.pose.orientation
                parts.append(f"{topic}=pos:({p.x:+.3f},{p.y:+.3f})")
        self.get_logger().info(" | ".join(parts))


def main(args=None):
    rclpy.init(args=args)
    node = DiagNavTopics()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
