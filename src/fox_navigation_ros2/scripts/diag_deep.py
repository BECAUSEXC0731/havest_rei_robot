#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度导航诊断：一次性输出定位、路径、激光、代价地图的关键信息，
用于判断"绿线正常但蓝线没有 / 机器人只转不走"的原因。

用法（导航运行中）：
    python3 src/fox_navigation_ros2/scripts/diag_deep.py

每 1 秒打印一行，包含：
    ROBOT_map / ROBOT_odom    机器人在 map 和 odom 系的位置(朝向)
    GOAL                      目标点
    PLAN  n/start/end         全局路径点数与首末点坐标
    LOCALPLAN n/start/end     局部路径点数与首末点坐标(蓝线)
    SCAN  min/@deg count<1m   激光最近点与 1m 内点数
    LOCALCOST obs/near/ring   局部代价地图障碍总数 / 0.8m内 / 0.3-0.9m环带
    CMD  vx/vy/vth            控制器下发速度

判断要点：
    - LOCALPLAN 一直只有几个点且首点在机器人附近 → DWB 只取到了脚下路径
    - LOCALPLAN 的点靠近 GOAL(远处) → 投影错乱，机器人被认为在路径末端附近
    - LOCALCOST 的 ring 很多(包围圈) → 激光近距假点围住机器人，DWB 只转不走
    - SCAN 的 min 距离偏小且 count<1m 很多 → 近距假点/障碍未滤干净
"""
import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path, Odometry
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class DiagDeep(Node):
    def __init__(self):
        super().__init__('diag_deep')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.last = {}
        self.subs = {
            '/plan': Path,
            '/transformed_global_plan': Path,
            '/local_plan': Path,
            '/global_costmap/costmap': OccupancyGrid,
            '/local_costmap/costmap': OccupancyGrid,
            '/cmd_vel': Twist,
            '/odom': Odometry,
            '/scan': LaserScan,
            '/goal_pose': PoseStamped,
        }
        for topic, typ in self.subs.items():
            self.last[topic] = None
            if typ is LaserScan:
                # LaserScan 发布通常用 Best Effort QoS，Reliable 订阅会收不到
                qos = rclpy.qos.QoSProfile(
                    depth=10,
                    reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT)
                self.create_subscription(typ, topic, self._cb(topic), qos)
            else:
                self.create_subscription(typ, topic, self._cb(topic), 10)
        self.create_timer(1.0, self.report)

    def _cb(self, topic):
        def cb(msg):
            self.last[topic] = msg
        return cb

    def _tf(self, target, source):
        try:
            t = self.tf_buffer.lookup_transform(target, source, rclpy.time.Time())
            p = t.transform.translation
            return (p.x, p.y, p.z, yaw_of(t.transform.rotation))
        except Exception:
            return None

    def report(self):
        out = []

        m = self._tf('map', 'base_footprint')
        if m:
            out.append(f"ROBOT_map=({m[0]:+.3f},{m[1]:+.3f}) yaw={math.degrees(m[3]):+.1f}")
        else:
            out.append("ROBOT_map=<无TF>")
        o = self._tf('odom', 'base_footprint')
        if o:
            out.append(f"ROBOT_odom=({o[0]:+.3f},{o[1]:+.3f}) yaw={math.degrees(o[3]):+.1f}")
        else:
            out.append("ROBOT_odom=<无TF>")

        g = self.last['/goal_pose']
        if g:
            p = g.pose.position
            out.append(f"GOAL=({p.x:+.3f},{p.y:+.3f})")

        plan = self.last['/plan']
        if plan and plan.poses:
            s = plan.poses[0].pose.position
            e = plan.poses[-1].pose.position
            out.append(f"PLAN n={len(plan.poses)} start=({s.x:+.2f},{s.y:+.2f}) end=({e.x:+.2f},{e.y:+.2f})")
        else:
            out.append("PLAN=<无>")

        # DWB 实际收到的路径（odom 系）——判断控制器拿到的路径是否正常
        tp = self.last['/transformed_global_plan']
        if tp and tp.poses:
            s = tp.poses[0].pose.position
            e = tp.poses[-1].pose.position
            out.append(
                f"TGP frame={tp.header.frame_id} n={len(tp.poses)} "
                f"start=({s.x:+.3f},{s.y:+.3f}) end=({e.x:+.3f},{e.y:+.3f})")
        else:
            out.append("TGP=<无>")

        lp = self.last['/local_plan']
        if lp and lp.poses:
            s = lp.poses[0].pose.position
            e = lp.poses[-1].pose.position
            out.append(
                f"LOCALPLAN n={len(lp.poses)} start=({s.x:+.3f},{s.y:+.3f}) end=({e.x:+.3f},{e.y:+.3f})")
        else:
            out.append("LOCALPLAN=<无>")

        sc = self.last['/scan']
        if sc:
            valid = [(r, i) for i, r in enumerate(sc.ranges)
                     if r < sc.range_max and r > 0.01]
            if valid:
                r, i = min(valid)
                ang = math.degrees(sc.angle_min + i * sc.angle_increment)
                n08 = sum(1 for rr, _ in valid if rr < 0.8)
                n10 = sum(1 for rr, _ in valid if rr < 1.0)
                n12 = sum(1 for rr, _ in valid if rr < 1.2)
                n15 = sum(1 for rr, _ in valid if rr < 1.5)
                npt = len(valid)
                out.append(
                    f"SCAN min={r:.3f}m @{ang:+.0f}deg n={npt} "
                    f"<0.8:{n08} 0.8-1.0:{n10-n08} 1.0-1.2:{n12-n10} 1.2-1.5:{n15-n12}")
            else:
                out.append("SCAN=无有效点")
        else:
            out.append("SCAN=<无>")

        cm = self.last['/local_costmap/costmap']
        if cm:
            w, h, res = cm.info.width, cm.info.height, cm.info.resolution
            ox, oy = cm.info.origin.position.x, cm.info.origin.position.y
            # 用机器人真实 odom 位置作中心（不能用窗口中心，滚动窗口中心≠机器人位置）
            rob = self._tf('odom', 'base_footprint')
            if rob:
                cx, cy = rob[0], rob[1]
            else:
                cx, cy = ox + w * res / 2.0, oy + h * res / 2.0
            obs = near = ring = 0
            for y in range(h):
                for x in range(w):
                    c = cm.data[y * w + x]
                    if c >= 99:
                        obs += 1
                        wx = ox + (x + 0.5) * res
                        wy = oy + (y + 0.5) * res
                        d = math.hypot(wx - cx, wy - cy)
                        if d < 0.8:
                            near += 1
                        if 0.3 < d < 0.9:
                            ring += 1
            out.append(f"LOCALCOST obs={obs} near<0.8m={near} ring0.3-0.9={ring}")
        else:
            out.append("LOCALCOST=<无>")

        c = self.last['/cmd_vel']
        if c:
            out.append(f"CMD vx={c.linear.x:+.3f} vy={c.linear.y:+.3f} vth={c.angular.z:+.3f}")

        self.get_logger().info(" | ".join(out))


def main(args=None):
    rclpy.init(args=args)
    node = DiagDeep()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
