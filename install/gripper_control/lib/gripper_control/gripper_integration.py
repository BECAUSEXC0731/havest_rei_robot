#!/usr/bin/env python3
"""
gripper_integration.py — 夹爪与机械臂集成桥接节点

将夹爪控制集成到现有的 arm_controller pick/place 流程中。
提供统一的抓取服务，自动协调机械臂移动 + 夹爪动作。

服务:
  /integrated_pick    [Move]  移动到目标 + 夹紧
  /integrated_place   [Move]  移动到目标 + 松开
  /integrated_grip    [SetBool]  true=夹紧 false=松开 (仅夹爪)

用法:
  ros2 run gripper_control gripper_integration.py
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.client import Client
from std_srvs.srv import SetBool

# 复用 arm_controller 的 Move.srv
from arm_controller.srv import Move


class GripperIntegration(Node):
    """协调机械臂 + 夹爪的集成节点"""

    def __init__(self):
        super().__init__('gripper_integration')

        # ======== 参数 ========
        self.declare_parameter('grip_delay', 0.5)   # 夹爪动作后等待(秒)
        self.declare_parameter('pre_grasp_offset_z', 30.0)  # 预抓取Z偏移(mm)
        self.declare_parameter('lift_height', 50.0)  # 抓取后抬升高度(mm)

        self.grip_delay = self.get_parameter('grip_delay').value
        self.pre_offset = self.get_parameter('pre_grasp_offset_z').value
        self.lift_height = self.get_parameter('lift_height').value

        # 使用独立回调组避免死锁
        self.cb_group = MutuallyExclusiveCallbackGroup()

        # ======== 客户端 ========
        # 等待服务可用
        self.cli_goto = self.create_client(Move, 'goto_position')
        self.cli_grip = self.create_client(SetBool, 'gripper/grip')

        # ======== 服务端 ========
        self.srv_pick = self.create_service(
            Move, 'integrated_pick', self.pick_callback, callback_group=self.cb_group)
        self.srv_place = self.create_service(
            Move, 'integrated_place', self.place_callback, callback_group=self.cb_group)
        self.srv_grip_only = self.create_service(
            SetBool, 'integrated_grip', self.grip_only_callback)

        self.get_logger().info("=" * 50)
        self.get_logger().info("夹爪集成节点已启动")
        self.get_logger().info("  服务: /integrated_pick  /integrated_place  /integrated_grip")
        self.get_logger().info("  预抓取偏移Z: +%.0fmm" % self.pre_offset)
        self.get_logger().info("  抓取后抬升: %.0fmm" % self.lift_height)
        self.get_logger().info("=" * 50)

    def _wait_for_services(self):
        """等待依赖的服务就绪"""
        self.get_logger().info("等待服务...")
        for name, cli in [('goto_position', self.cli_goto), ('gripper/grip', self.cli_grip)]:
            if not cli.wait_for_service(timeout_sec=5.0):
                self.get_logger().warn(f"服务 {name} 不可用!")
                return False
            self.get_logger().info(f"  ✅ {name} 就绪")
        return True

    def _call_goto(self, x, y, z, roll=0.0):
        """调用机械臂移动到目标位置"""
        req = Move.Request()
        req.pose.position.x = float(x)
        req.pose.position.y = float(y)
        req.pose.position.z = float(z)
        req.pose.roll = float(roll)
        future = self.cli_goto.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def _call_grip(self, close: bool):
        """控制夹爪: True=夹紧 False=松开"""
        req = SetBool.Request()
        req.data = close
        future = self.cli_grip.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def pick_callback(self, req, res):
        """
        抓取流程:
        1. 移动到目标上方 (预抓取位置)
        2. 下降到目标位置
        3. 夹紧
        4. 抬升
        """
        if not self._wait_for_services():
            res.success = False
            res.message = "服务不可用"
            return res

        x, y, z = req.pose.position.x, req.pose.position.y, req.pose.position.z
        roll = req.pose.roll
        self.get_logger().info(f"[抓取] 目标 ({x:.1f}, {y:.1f}, {z:.1f})")

        # 1. 预抓取位置（目标上方）
        pre_z = z + self.pre_offset
        self.get_logger().info(f"  步骤1: 移动到预抓取位 ({x:.1f}, {y:.1f}, {pre_z:.1f})")
        r = self._call_goto(x, y, pre_z, roll)
        if not r or not r.success:
            res.success = False
            res.message = "预抓取定位失败"
            return res

        # 2. 下降到目标位置
        self.get_logger().info(f"  步骤2: 下降到目标 ({x:.1f}, {y:.1f}, {z:.1f})")
        r = self._call_goto(x, y, z, roll)
        if not r or not r.success:
            res.success = False
            res.message = "目标定位失败"
            return res

        # 3. 夹紧
        self.get_logger().info(f"  步骤3: 夹紧")
        r = self._call_grip(True)
        if not r or not r.success:
            res.success = False
            res.message = "夹爪失败"
            return res
        self._sleep(self.grip_delay)

        # 4. 抬升
        lift_z = z + self.lift_height
        self.get_logger().info(f"  步骤4: 抬升 ({x:.1f}, {y:.1f}, {lift_z:.1f})")
        r = self._call_goto(x, y, lift_z, roll)

        res.success = True
        res.message = "抓取完成"
        self.get_logger().info("✅ 抓取完成")
        return res

    def place_callback(self, req, res):
        """
        放置流程:
        1. 移动到目标上方
        2. 下降到目标位置
        3. 松开夹爪
        4. 抬升
        """
        if not self._wait_for_services():
            res.success = False
            res.message = "服务不可用"
            return res

        x, y, z = req.pose.position.x, req.pose.position.y, req.pose.position.z
        roll = req.pose.roll
        self.get_logger().info(f"[放置] 目标 ({x:.1f}, {y:.1f}, {z:.1f})")

        # 1. 预放置位置
        pre_z = z + self.pre_offset
        r = self._call_goto(x, y, pre_z, roll)
        if not r or not r.success:
            res.success = False
            res.message = "预放置定位失败"
            return res

        # 2. 下降到目标
        r = self._call_goto(x, y, z, roll)
        if not r or not r.success:
            res.success = False
            res.message = "放置定位失败"
            return res

        # 3. 松开
        r = self._call_grip(False)
        self._sleep(self.grip_delay)

        # 4. 抬升
        lift_z = z + self.lift_height
        r = self._call_goto(x, y, lift_z, roll)

        res.success = True
        res.message = "放置完成"
        self.get_logger().info("✅ 放置完成")
        return res

    def grip_only_callback(self, req, res):
        """仅控制夹爪 (不移动机械臂)"""
        action = "夹紧" if req.data else "松开"
        self.get_logger().info(f"[夹爪] {action}")
        r = self._call_grip(req.data)
        if r:
            res.success = r.success
            res.message = r.message
        else:
            res.success = False
        return res

    def _sleep(self, sec):
        """安全等待"""
        try:
            import time
            time.sleep(sec)
        except KeyboardInterrupt:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = GripperIntegration()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
