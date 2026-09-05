"""
机械臂 + 夹爪控制接口
封装对 arm_controller 的 goto_position/home 服务，以及 gripper_control 的夹爪服务。
抓取采用夹爪(gripper/grip)夹紧/松开，不使用气泵(pick/place/pump)。
"""
import time
import rclpy
from rclpy.node import Node
from arm_controller.srv import Move
from std_srvs.srv import SetBool


class ArmInterface:
    """机械臂 + 夹爪控制高层接口。"""

    def __init__(self, node: Node, timeout_sec: float = 30.0,
                 grip_delay: float = 1.0):
        self.node = node
        self.timeout = timeout_sec
        self.grip_delay = grip_delay
        self.logger = node.get_logger()

        # 创建服务客户端
        self.goto_cli = node.create_client(Move, 'goto_position')
        self.grip_cli = node.create_client(SetBool, 'gripper/grip')
        self.home_cli = node.create_client(SetBool, 'home')

        # 等待服务可用
        self._wait_services()

    def _wait_services(self):
        services = {
            'goto_position': self.goto_cli,
            'gripper/grip': self.grip_cli,
            'home': self.home_cli,
        }
        for name, cli in services.items():
            if not cli.wait_for_service(timeout_sec=5.0):
                self.logger.warn(f"⚠ 服务 {name} 不可用，抓取功能可能受限")

    def goto(self, x_mm: float, y_mm: float, z_mm: float,
             roll: float = -1.0) -> bool:
        """移动到绝对位置（毫米）。"""
        req = Move.Request()
        req.pose.position.x = float(x_mm)
        req.pose.position.y = float(y_mm)
        req.pose.position.z = float(z_mm)
        req.pose.roll = float(roll)
        future = self.goto_cli.call_async(req)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=self.timeout)
        if future.done() and future.result() is not None:
            return future.result().success
        return False

    def grip(self, close: bool) -> bool:
        """控制夹爪: close=True 夹紧, close=False 松开 (gripper/grip 服务)。"""
        req = SetBool.Request()
        req.data = close
        future = self.grip_cli.call_async(req)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)
        if future.done() and future.result() is not None:
            return future.result().success
        return False

    def home(self) -> bool:
        """回到安全位置 (200, 0, 150)。"""
        req = SetBool.Request()
        req.data = True
        future = self.home_cli.call_async(req)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=self.timeout)
        if future.done() and future.result() is not None:
            return future.result().success
        return False

    # ─── 高层组合动作 ───

    def pick_at(self, x_mm: float, y_mm: float, z_mm: float,
                lift_height: float = 50.0) -> bool:
        """
        在指定位置执行夹爪抓取流程(参考 grape_grasp_test.py):
        1. 上升到安全高度
        2. 下降到目标
        3. 夹爪夹紧
        4. 抬升(保持夹住)
        """
        safe_z = max(z_mm, 80.0) + lift_height

        # 1. 移动到上方安全高度
        self.logger.info(f"  上升至安全高度: ({x_mm:.0f}, {y_mm:.0f}, {safe_z:.0f})")
        if not self.goto(x_mm, y_mm, safe_z):
            self.logger.warn("  安全高度不可达")
            return False

        # 2. 下降到目标
        self.logger.info(f"  下降到目标: ({x_mm:.0f}, {y_mm:.0f}, {z_mm:.0f})")
        if not self.goto(x_mm, y_mm, z_mm):
            self.logger.warn("  下降失败")
            return False
        time.sleep(0.5)

        # 3. 夹爪夹紧
        self.logger.info(f"  夹爪夹紧: ({x_mm:.0f}, {y_mm:.0f}, {z_mm:.0f})")
        if not self.grip(True):
            self.logger.warn("  夹爪夹紧失败")
            return False
        time.sleep(self.grip_delay)

        # 4. 抬升
        self.logger.info(f"  抬升到: ({x_mm:.0f}, {y_mm:.0f}, {safe_z:.0f})")
        self.goto(x_mm, y_mm, safe_z)
        return True

    def place_at(self, x_mm: float, y_mm: float, z_mm: float,
                 lift_height: float = 50.0) -> bool:
        """
        在指定位置放置(夹爪松开):
        1. 移动到上方安全高度
        2. 下降到目标
        3. 夹爪松开
        4. 抬升
        """
        safe_z = max(z_mm, 80.0) + lift_height

        self.logger.info(f"  移动到放置位置上方: ({x_mm:.0f}, {y_mm:.0f}, {safe_z:.0f})")
        if not self.goto(x_mm, y_mm, safe_z):
            self.logger.warn("  放置安全高度不可达")
            return False

        self.logger.info(f"  下降到放置位置: ({x_mm:.0f}, {y_mm:.0f}, {z_mm:.0f})")
        if not self.goto(x_mm, y_mm, z_mm):
            self.logger.warn("  下降失败")
            return False
        time.sleep(0.5)

        self.logger.info("  夹爪松开")
        if not self.grip(False):
            self.logger.warn("  夹爪松开失败")
            return False
        time.sleep(0.3)

        self.logger.info(f"  抬升")
        self.goto(x_mm, y_mm, safe_z)
        return True
