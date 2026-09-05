#!/usr/bin/env python3
"""
D2C 深度对齐验证探针（不需要 YOLO 模型）

鼠标点击 RGB 图任意像素 → 显示：
  - 该像素经手动 D2C 映射取到的深度(相机系 z)
  - 3D 坐标（彩色系、机器人系 mm）

验证方法：
  1. 相机 color+depth 双流启动（不带 depth_registration）
  2. 把物体(棋盘格/葡萄)放在相机正前方，用尺子量出它到相机的距离
  3. python3 src/calibration/d2c_probe.py
  4. 点击物体中心，看报出的 depth 是否 ≈ 尺子量的距离

按键: 鼠标左键=探测   q=退出
"""
import sys
import os
import numpy as np
import cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

ROOT = '/home/ubuntu/ros2fox'
sys.path.insert(0, os.path.join(ROOT, 'src'))
from fox_grape_harvest.depth_utils import (
    load_hand_eye_calibration, load_d2c_config,
    color_pixel_to_camera_3d, camera_to_robot_3d
)

HAND_EYE = os.path.join(ROOT, 'calib_result', 'hand_eye_result.json')
EXTRINSIC = os.path.join(ROOT, 'calib_result', 'color_ir_extrinsic.json')
IR_INFO = os.path.join(ROOT, 'calib_data', 'ir', 'ir_camera_info.yaml')


class D2CProbe(Node):
    def __init__(self):
        super().__init__('d2c_probe')
        self.bridge = CvBridge()
        self.rgb = None
        self.depth = None
        self.K_color = None
        self.click = None

        self.T_cam_to_robot = load_hand_eye_calibration(HAND_EYE)
        d2c = load_d2c_config(EXTRINSIC, IR_INFO)
        if d2c is None:
            self.get_logger().error("未找到手动对齐配置，先跑 calibrate_color_ir.py")
            self.K_ir = None
            self.T_color_to_ir = None
        else:
            self.K_ir, self.T_color_to_ir = d2c
            self.get_logger().info("已加载手动 D2C 配置")

        self.create_subscription(Image, '/camera/color/image_raw',
                                 self.rgb_cb, qos_profile_sensor_data)
        self.create_subscription(Image, '/camera/depth/image_raw',
                                 self.depth_cb, qos_profile_sensor_data)
        self.create_subscription(CameraInfo, '/camera/color/camera_info',
                                 self.info_cb, 1)

    def rgb_cb(self, msg):
        try:
            self.rgb = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass

    def depth_cb(self, msg):
        try:
            d = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if d.dtype == np.uint16:
                d = d.astype(np.float32) / 1000.0
            self.depth = d
        except Exception:
            pass

    def info_cb(self, msg):
        if self.K_color is None:
            k = np.array(msg.k).reshape(3, 3)
            if k[0, 0] > 100 and not np.any(np.isnan(k)):
                self.K_color = k

    def probe(self, u, v):
        if self.K_ir is None or self.K_color is None or self.depth is None:
            return None
        pt_cam = color_pixel_to_camera_3d(u, v, self.depth, self.K_color,
                                          self.K_ir, self.T_color_to_ir)
        if pt_cam is None:
            return None
        pt_robot = camera_to_robot_3d(pt_cam, self.T_cam_to_robot)
        return pt_cam, pt_robot

    def run(self):
        win = 'D2C Probe (click pixel, q quit)'
        cv2.namedWindow(win)

        def mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.click = (x, y)

        cv2.setMouseCallback(win, mouse)
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.rgb is None:
                cv2.waitKey(30)
                continue
            img = self.rgb.copy()
            if self.click is not None:
                u, v = self.click
                res = self.probe(u, v)
                if res is not None:
                    pt_cam, pt_robot = res
                    txt = (f"depth={pt_cam[2]*1000:.0f}mm  "
                           f"cam=({pt_cam[0]*1000:.0f},{pt_cam[1]*1000:.0f},{pt_cam[2]*1000:.0f})  "
                           f"robot=({pt_robot[0]*1000:.0f},{pt_robot[1]*1000:.0f},{pt_robot[2]*1000:.0f})mm")
                    self.get_logger().info(f"像素({u},{v}) " + txt)
                    cv2.drawMarker(img, (u, v), (0, 0, 255), cv2.MARKER_CROSS, 16, 3)
                    cv2.putText(img, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)
                else:
                    self.get_logger().warn(f"像素({u},{v}) 无有效深度")
                self.click = None
            cv2.imshow(win, img)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()


def main():
    rclpy.init()
    node = D2CProbe()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
