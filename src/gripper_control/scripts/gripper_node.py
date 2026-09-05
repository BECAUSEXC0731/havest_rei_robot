#!/usr/bin/env python3
"""
gripper_node.py — 众灵(ZL-Robot)总线舵机夹爪 ROS2 控制节点

使用 ASCII 文本协议通过串口控制舵机:
  #IDP脉冲T时间!   角度控制
  #IDPRAD!         读取角度
  #IDPID!          检测ID

默认:
  - 串口: /dev/ttyGripper (udev 绑定 CH340, 可通过参数修改)
  - 波特率: 115200
  - 舵机 ID: 1 (可通过参数修改)
  - 脉宽范围: 500(松开) ~ 2000(抓紧), 中位1250
  - 实测(2026-08-08): 2000+ = 抓紧(闭合), 500 = 松开(张开)

服务:
  /gripper/grip  [std_srvs/SetBool]  true=抓紧(闭合)  false=松开(张开)
"""

import os
import sys
import time

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class GripperNode(Node):
    """
    夹爪控制节点
    将舵机脉宽映射到夹爪开口 (实测):
      2000 → 抓紧 (闭合)
      500  → 松开 (张开)
    """

    def __init__(self):
        super().__init__('gripper_node')

        # ======== 参数 ========
        self.declare_parameter('port', '/dev/ttyGripper')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('servo_id', 1)
        # 实测(2026-08-08): 2000 = 抓紧(闭合), 500 = 松开(张开)
        self.declare_parameter('pulse_min', 500)    # 松开
        self.declare_parameter('pulse_max', 2000)   # 抓紧
        self.declare_parameter('pulse_mid', 1250)   # 中位
        self.declare_parameter('move_time_ms', 1500)  # 动作时间(ms)

        # 自动检测串口: 只认夹爪 CH340 (1a86:7523), 绝不用普通 /dev/ttyUSB* 兜底!
        # 否则 CH340 缺失时会误选到雷达/底盘的 CP210x, 把夹爪指令发错设备(危险)!
        import glob as _glob
        import subprocess as _sp

        def _is_ch340(path: str) -> bool:
            """判断该 tty 是否对应夹爪 CH340 (idVendor=1a86, idProduct=7523)"""
            try:
                r = _sp.run(['udevadm', 'info', '-q', 'property', '-n', path],
                            capture_output=True, text=True, timeout=3)
                props = r.stdout
                return ('ID_VENDOR_ID=1a86' in props) and ('ID_MODEL_ID=7523' in props)
            except Exception:
                return False

        param_port = self.get_parameter('port').value
        port = None
        # 1) 参数显式指定且存在
        if param_port and os.path.exists(param_port):
            port = param_port
        # 2) udev 绑定软链接 (夹爪专用, 由 99-gripper.rules 生成)
        if port is None and os.path.exists('/dev/ttyGripper'):
            port = '/dev/ttyGripper'
        # 3) 扫描所有候选, 用 VID/PID 精确识别 CH340 (兼容 ttyUSB*/ttyCH341USB* 命名)
        if port is None:
            for c in sorted(_glob.glob('/dev/ttyUSB*') + _glob.glob('/dev/ttyCH341USB*')):
                if _is_ch340(c):
                    port = c
                    break
        if port is None:
            self.get_logger().error(
                "未找到夹爪 CH340 (1a86:7523)! 请检查: lsusb 是否能看到、USB 线/转接板是否正常。"
                "为避免误选雷达/底盘, 本次不启用夹爪串口。")
            port = param_port or '/dev/ttyGripper'  # 指向不存在设备, 后续命令会明确报错
        self.port = port
        self.get_logger().info(f"选定串口: {port}")
        baud = self.get_parameter('baudrate').value
        self.servo_id = self.get_parameter('servo_id').value
        self.p_min = self.get_parameter('pulse_min').value
        self.p_max = self.get_parameter('pulse_max').value
        self.p_mid = self.get_parameter('pulse_mid').value
        self.move_time = self.get_parameter('move_time_ms').value

        self.current_pulse = self.p_mid  # 当前脉宽

        # ======== 串口 ========
        # 不使用 pyserial, 直接用 os.open/write 模仿 echo 命令
        self.get_logger().info(f"串口: {port} @ {baud}")
        self.get_logger().info("注意: CH340 TX 和 RX 需要短接后接舵机信号线!")

        # 用 subprocess 调 stty 配置串口 (和手动测试完全一致)
        import subprocess as _sp
        self._stty_cmd = ['stty', '-F', port, str(baud), 'cs8',
                          '-cstopb', '-parenb', 'raw', '-echo']
        try:
            _sp.run(self._stty_cmd, capture_output=True, check=True)
            self.get_logger().info(f"端口 {port} 已配置 ✅")
        except Exception as e:
            self.get_logger().error(f"端口 {port} 配置失败: {e}")

        # ======== 服务 ========
        self.srv_grip = self.create_service(SetBool, 'gripper/grip', self.grip_callback)

        self.get_logger().info("=" * 50)
        self.get_logger().info(f"夹爪控制节点已启动")
        self.get_logger().info(f"  串口: {port}")
        self.get_logger().info(f"  舵机ID: {self.servo_id}")
        self.get_logger().info(f"  脉宽范围: {self.p_min}(松开) ~ {self.p_max}(抓紧)")
        self.get_logger().info("服务: /gripper/grip (true=抓紧 false=松开)")
        self.get_logger().info("=" * 50)

    # ============================================================
    # 串口通信 - 完全复用 echo 命令的方式
    # ============================================================
    def _send_raw(self, cmd_str: str):
        import subprocess
        safe = cmd_str.replace("'", "'\\''")
        shell_cmd = f"echo -en '{safe}\\n' > {self.port}"
        self.get_logger().info(f"[shell] {shell_cmd}")
        r = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            self.get_logger().error(f"[失败] {r.stderr}")
        else:
            self.get_logger().info(f"[完成] {cmd_str!r}")

    def grip_callback(self, req, res):
        self.get_logger().info(f"[回调] data={req.data}  p_min={self.p_min}  p_max={self.p_max}")

        if req.data:
            pulse = self.p_max
            action = "抓"
        else:
            pulse = self.p_min
            action = "松"

        self.get_logger().info(f"[执行] action={action}  pulse={pulse}")

        cmd_str = f"#{self.servo_id:03d}P{pulse:04d}T{self.move_time}!"
        self._send_raw(cmd_str)
        self.current_pulse = pulse

        self.get_logger().info(f"夹爪: {action}  pulse={pulse}")
        res.success = True
        res.message = f"pulse={pulse}"
        return res

    def set_state_callback(self, req, res):
        return self.grip_callback(req, res)


def main(args=None):
    rclpy.init(args=args)
    node = GripperNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
