#!/usr/bin/env python3
"""
FOX 机器人底盘 Python 驱动 (ROS2)
替代 C++ 版 rei_robot_base，通过 Modbus RTU 驱动底盘
"""
import rclpy
import serial
import struct
import time
import math
import crcmod.predefined
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, TransformStamped
from tf2_ros import TransformBroadcaster

# ─── 运动学常量 ───
PI = 3.1415926


class FoxBaseDriver(Node):
    def __init__(self):
        super().__init__('fox_base_driver')

        # 参数
        self.declare_parameter('port', '/dev/fox')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('kinematics_mode', 3)
        self.declare_parameter('wheel_radius', 0.0401)
        self.declare_parameter('wheel_separation_x', 0.270)
        self.declare_parameter('motors_index', [0, 1, 2])
        self.declare_parameter('motors_signs', [-1.0, -1.0, -1.0])
        self.declare_parameter('max_vel_x', 0.8)
        self.declare_parameter('max_vel_y', 0.8)
        self.declare_parameter('max_vel_th', 1.5)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('publish_odom', True)
        self.declare_parameter('publish_odom_tf', True)

        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.kin_mode = self.get_parameter('kinematics_mode').value
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_sep_x = self.get_parameter('wheel_separation_x').value
        self.motors_index = self.get_parameter('motors_index').value
        self.motors_signs = self.get_parameter('motors_signs').value
        self.max_vx = self.get_parameter('max_vel_x').value
        self.max_vy = self.get_parameter('max_vel_y').value
        self.max_vth = self.get_parameter('max_vel_th').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.publish_odom = self.get_parameter('publish_odom').value
        self.publish_tf = self.get_parameter('publish_odom_tf').value

        # 运动学转换因子
        self.vel2rpm = 60.0 * 0.5 / PI / self.wheel_radius
        self.rpm2vel = 2.0 * PI / 60.0 * self.wheel_radius

        # 里程计
        self.odom_x = 0.0
        self.odom_y = 0.0
        self.odom_th = 0.0
        self.last_time = None

        # 软急停
        self.soft_estop = False

        # 串口
        self.ser = None
        self.crc16 = crcmod.predefined.mkCrcFun('modbus')

        # 发布者
        self.odom_pub = self.create_publisher(Odometry, '/odom', 50)
        self.tf_broadcaster = TransformBroadcaster(self)

        # 订阅者
        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 1)

        # 连接底盘
        self.connect()

        if self.ser:
            self.get_logger().info('底盘驱动已启动，50Hz 控制循环')
            self.create_timer(0.02, self.update)  # 50Hz
            self.create_timer(0.5, self.keep_alive)  # 2Hz 心跳保活
        else:
            self.get_logger().error('无法连接底盘，驱动未启动')

    def connect(self):
        """连接底盘串口"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.3)
            self.ser.dtr = 0
            self.ser.rts = 0
            time.sleep(0.5)
            self.get_logger().info(f'串口已连接: {self.port} @ {self.baudrate}')
            # 发送停止指令
            self.send_motor_speed([0.0, 0.0, 0.0, 0.0])
        except Exception as e:
            self.get_logger().error(f'串口连接失败: {e}')
            self.ser = None

    def send_modbus_request(self, req_bytes, resp_len=20):
        """发送Modbus请求并读取响应"""
        if not self.ser:
            return None
        try:
            # 等待残留响应排空
            time.sleep(0.05)
            self.ser.reset_input_buffer()
            self.ser.write(req_bytes)
            time.sleep(0.1)
            resp = self.ser.read(resp_len)
            # 如果读到的是写响应（0x10），重试一次
            if resp and len(resp) > 1 and resp[1] == 0x10:
                time.sleep(0.1)
                self.ser.reset_input_buffer()
                # 重发原请求
                self.ser.write(req_bytes)
                time.sleep(0.1)
                resp = self.ser.read(resp_len)
            return resp
        except:
            return None

    def read_holding_registers(self, addr, count):
        """读取保持寄存器 (Modbus 功能码 0x03)"""
        req = bytes([0x01, 0x03, addr >> 8, addr & 0xFF, count >> 8, count & 0xFF])
        crc = self.crc16(req)
        req += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        resp = self.send_modbus_request(req, count * 2 + 5)
        if resp and len(resp) >= 3 and resp[0] == 0x01 and resp[1] == 0x03:
            byte_cnt = resp[2]
            if byte_cnt == count * 2:
                values = []
                for i in range(count):
                    hi = resp[3 + i * 2]
                    lo = resp[4 + i * 2]
                    values.append((hi << 8) | lo)
                return values
        return None

    def read_input_registers(self, addr, count):
        """读取输入寄存器 (Modbus 功能码 0x04)"""
        req = bytes([0x01, 0x04, addr >> 8, addr & 0xFF, count >> 8, count & 0xFF])
        crc = self.crc16(req)
        req += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        resp = self.send_modbus_request(req, count * 2 + 5)
        if resp and len(resp) >= 3 and resp[0] == 0x01 and resp[1] == 0x04:
            byte_cnt = resp[2]
            if byte_cnt == count * 2:
                values = []
                for i in range(count):
                    hi = resp[3 + i * 2]
                    lo = resp[4 + i * 2]
                    values.append((hi << 8) | lo)
                return values
        return None

    def write_holding_registers(self, addr, values):
        """写入保持寄存器 (Modbus 功能码 0x10)"""
        count = len(values)
        byte_count = count * 2
        req = bytes([0x01, 0x10, addr >> 8, addr & 0xFF, count >> 8, count & 0xFF, byte_count])
        for v in values:
            req += bytes([(v >> 8) & 0xFF, v & 0xFF])
        crc = self.crc16(req)
        req += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        resp = self.send_modbus_request(req, 8)
        return resp is not None and len(resp) >= 6

    def send_motor_speed(self, speeds_rpm):
        """发送电机目标转速 (RPM) 到保持寄存器 0-15 (4个double)"""
        regs = []
        for s in speeds_rpm:
            # double 转 4个 uint16 (大端序)
            packed = struct.pack('>d', float(s))
            for i in range(0, 8, 2):
                regs.append((packed[i] << 8) | packed[i + 1])
        # 补足16个寄存器
        while len(regs) < 16:
            regs.append(0)
        return self.write_holding_registers(0, regs[:16])

    def get_motor_speed(self):
        """读取电机当前转速 (RPM) 从保持寄存器 0-15"""
        values = self.read_holding_registers(0, 16)
        if not values or len(values) < 16:
            return None
        speeds = []
        for i in range(4):
            idx = i * 4
            packed = bytes([(values[idx] >> 8) & 0xFF, values[idx] & 0xFF,
                           (values[idx + 1] >> 8) & 0xFF, values[idx + 1] & 0xFF,
                           (values[idx + 2] >> 8) & 0xFF, values[idx + 2] & 0xFF,
                           (values[idx + 3] >> 8) & 0xFF, values[idx + 3] & 0xFF])
            speed = struct.unpack('>d', packed)[0]
            speeds.append(speed)
        return speeds

    def get_battery_voltage(self):
        """读取电池电压 (输入寄存器 addr=17)"""
        vals = self.read_input_registers(17, 1)
        if vals:
            return vals[0] / 1000.0
        return None

    # ─── 运动学 ───
    def forward_kinematics(self, motor_speed):
        """正运动学: 电机RPM → 机器人速度 (vx, vy, vth)"""
        b = 1.0 / math.sqrt(3.0)
        a = 1.0 / 3.0
        c = 1.0 / self.wheel_sep_x / 3.0

        m = [motor_speed[self.motors_index[i]] * self.motors_signs[self.motors_index[i]]
             for i in range(3)]

        vx = (b * m[0] - b * m[1]) * self.rpm2vel
        vy = (a * m[0] + a * m[1] - 2.0 * a * m[2]) * self.rpm2vel
        vth = (c * m[0] + c * m[1] + c * m[2]) * self.rpm2vel
        return vx, vy, vth

    def inverse_kinematics(self, vx, vy, vth):
        """逆运动学: 机器人速度 → 电机RPM"""
        sq3 = math.sqrt(3.0) * 0.5
        m0 = (sq3 * vx + 0.5 * vy + self.wheel_sep_x * vth) * self.vel2rpm
        m1 = (-sq3 * vx + 0.5 * vy + self.wheel_sep_x * vth) * self.vel2rpm
        m2 = (-1.0 * vy + self.wheel_sep_x * vth) * self.vel2rpm

        motor = [0.0, 0.0, 0.0, 0.0]
        motor[self.motors_index[0]] = m0 * self.motors_signs[self.motors_index[0]]
        motor[self.motors_index[1]] = m1 * self.motors_signs[self.motors_index[1]]
        motor[self.motors_index[2]] = m2 * self.motors_signs[self.motors_index[2]]
        return motor

    # ─── 回调 ───
    def cmd_vel_callback(self, msg):
        vx = max(-self.max_vx, min(self.max_vx, msg.linear.x))
        vy = max(-self.max_vy, min(self.max_vy, msg.linear.y))
        vth = max(-self.max_vth, min(self.max_vth, msg.angular.z))
        motor_speeds = self.inverse_kinematics(vx, vy, vth)
        motor_str = ', '.join([f'{s:.1f}' for s in motor_speeds])
        self.get_logger().info(f'cmd_vel: vx={vx:.2f} vy={vy:.2f} vth={vth:.2f}  motor=[{motor_str}]')
        self.send_motor_speed(motor_speeds)

    # ─── 主循环 ───
    def keep_alive(self):
        """心跳保活：定期发送0速度防止看门狗超时"""
        if self.ser:
            self.send_motor_speed([0.0, 0.0, 0.0, 0.0])

    def update(self):
        if not self.ser:
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9 if self.last_time else 0.02
        self.last_time = now

        # 读取电机转速（失败不影响，只是没里程计数据）
        speeds = self.get_motor_speed()
        if speeds is None:
            return

        # 正运动学
        vx, vy, vth = self.forward_kinematics(speeds)
        # 电机编码器反馈符号与运动学模型相反，对 vx 取反
        vx = -vx

        # 里程计积分
        dx = (vx * math.cos(self.odom_th) - vy * math.sin(self.odom_th)) * dt
        dy = (vx * math.sin(self.odom_th) + vy * math.cos(self.odom_th)) * dt
        dth = vth * dt

        self.odom_x += dx
        self.odom_y += dy
        self.odom_th += dth

        # 发布里程计
        if self.publish_odom:
            odom = Odometry()
            odom.header.stamp = now.to_msg()
            odom.header.frame_id = self.odom_frame
            odom.child_frame_id = self.base_frame
            odom.pose.pose.position.x = self.odom_x
            odom.pose.pose.position.y = self.odom_y
            odom.pose.pose.orientation.z = math.sin(self.odom_th / 2)
            odom.pose.pose.orientation.w = math.cos(self.odom_th / 2)
            odom.twist.twist.linear.x = vx
            odom.twist.twist.linear.y = vy
            odom.twist.twist.angular.z = vth
            self.odom_pub.publish(odom)

        # 发布 TF
        if self.publish_tf:
            t = TransformStamped()
            t.header.stamp = now.to_msg()
            t.header.frame_id = self.odom_frame
            t.child_frame_id = self.base_frame
            t.transform.translation.x = self.odom_x
            t.transform.translation.y = self.odom_y
            t.transform.rotation.z = math.sin(self.odom_th / 2)
            t.transform.rotation.w = math.cos(self.odom_th / 2)
            self.tf_broadcaster.sendTransform(t)


def main(args=None):
    print('=== FoxBaseDriver 启动 ===', flush=True)
    rclpy.init(args=args)
    print('rclpy.init OK', flush=True)
    node = FoxBaseDriver()
    print('节点创建成功', flush=True)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
