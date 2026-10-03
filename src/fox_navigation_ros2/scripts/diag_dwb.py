#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看 DWB 控制器的轨迹评分（发布在 /trajectories），
判断"为什么只选旋转轨迹不前进"。

用法（导航运行中、已给目标点）：
    python3 src/fox_navigation_ros2/scripts/diag_dwb.py

每 1 秒打印评分最高的几条轨迹：
    #0 vx=0.000 vy=0.000 vth=0.800 total=... [critic:score ...]

判断：
    - 最优轨迹 vth 大而 vx=0 → DWB 在选旋转；看是哪个 critic 把前进轨迹评低了
    - 若 BaseObstacle 把 vx>0 轨迹评为高(差)分 → 代价地图判前进撞障
    - 若 PathAlign/GoalAlign 把 vx>0 评为高(差)分 → 路径方向/朝向问题
"""
import math

import rclpy
from rclpy.node import Node
from dwb_msgs.msg import LocalPlanEvaluation
from nav_msgs.msg import Odometry, Path


class DiagDWB(Node):
    def __init__(self):
        super().__init__('diag_dwb')
        self.last = None
        self.odom = None
        self.tgp = None
        # DWB 的轨迹评分发布在 /evaluation（publish_evaluation 默认 true）
        self.create_subscription(LocalPlanEvaluation, '/evaluation', self.cb, 10)
        self.create_subscription(Odometry, '/odom', lambda m: setattr(self, 'odom', m), 10)
        self.create_subscription(Path, '/transformed_global_plan',
                                 lambda m: setattr(self, 'tgp', m), 10)
        self.create_timer(1.0, self.report)

    def cb(self, msg):
        self.last = msg

    @staticmethod
    def _yaw(q):
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                          1.0 - 2.0 * (q.y * q.y + q.z * q.z))

    def _fmt(self, e):
        t = e.traj
        v = t.velocity
        scores = ", ".join(f"{s.name}:{s.raw_score:.2f}" for s in e.scores)
        return (f"vx={v.x:+.3f} vy={v.y:+.3f} vth={v.theta:+.3f} "
                f"total={e.total:+.3f} [{scores}]")

    def report(self):
        # 机器人朝向 vs 目标方向偏差（判断 GoalAlign 为什么恒定高）
        head = []
        if self.odom and self.tgp and self.tgp.poses:
            o = self.odom.pose.pose
            robot = (o.position.x, o.position.y)
            yaw = self._yaw(o.orientation)
            g = self.tgp.poses[-1].pose.position
            target_dir = math.atan2(g.y - robot[1], g.x - robot[0])
            diff = math.degrees(target_dir - yaw)
            # 归一化到 [-180, 180]
            diff = (diff + 180) % 360 - 180
            head.append(
                f"ROBOT_yaw={math.degrees(yaw):+.1f} TARGET_dir={math.degrees(target_dir):+.1f} "
                f"偏差={diff:+.1f}deg (TGPend=({g.x:+.2f},{g.y:+.2f}))")
        else:
            head.append("朝向/目标=<无>")

        if self.last is None:
            self.get_logger().info(head[0] + " | 无 /evaluation 数据（需已给目标点）")
            return
        twists = self.last.twists
        if not twists:
            self.get_logger().info(head[0] + " | /evaluation 为空（可能 NoLegalTrajectories）")
            return
        bi = self.last.best_index
        # 统计所有采样轨迹的 vx 分布（确认前进轨迹是否被生成）
        vxs = sorted({round(e.traj.velocity.x, 3) for e in twists})
        vx_pos = sum(1 for e in twists if e.traj.velocity.x > 0.01)
        vx_zero = sum(1 for e in twists if abs(e.traj.velocity.x) <= 0.01)
        vx_neg = sum(1 for e in twists if e.traj.velocity.x < -0.01)
        self.get_logger().info(
            f"[vx采样] n={len(twists)} vx>0:{vx_pos} vx=0:{vx_zero} vx<0:{vx_neg} | "
            f"vx值={vxs[:10]}")
        fwd = [i for i, e in enumerate(twists) if e.traj.velocity.x > 0.01]
        rot = [i for i, e in enumerate(twists)
               if abs(e.traj.velocity.x) < 0.01 and abs(e.traj.velocity.theta) > 0.1]
        best_fwd = min(fwd, key=lambda i: twists[i].total) if fwd else None
        out = [f"BEST(idx{bi}) {self._fmt(twists[bi])}"]
        if best_fwd is not None:
            out.append(f"BEST_FWD(idx{best_fwd}) {self._fmt(twists[best_fwd])}")
        if rot:
            best_rot = min(rot, key=lambda i: twists[i].total)
            out.append(f"BEST_ROT(idx{best_rot}) {self._fmt(twists[best_rot])}")
        top = sorted(range(len(twists)), key=lambda i: twists[i].total)[:3]
        out.append("TOP3: " + " || ".join(f"#{i}{self._fmt(twists[i])}" for i in top))
        self.get_logger().info(head[0] + " | " + " | ".join(out))


def main(args=None):
    rclpy.init(args=args)
    node = DiagDWB()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
