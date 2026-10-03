#!/usr/bin/env python3
"""
ArUco 实时检测查看器 —— 诊断"识别不到码"问题

显示相机彩色画面，实时叠加检测到的 ArUco 标记（ID 和边框），
并在终端打印检测到的 ID 列表，帮你判断：
  1. 相机画面是否正常
  2. 标记是否在视野内 / 是否太小 / 是否太暗
  3. 用的字典 DICT_4X4_100 能否识别出你的标记

用法:
  python3 src/calibration/aruco_view.py

按键:
  ESC 退出
"""
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class ArucoView(Node):
    def __init__(self):
        super().__init__('aruco_view')
        self.bridge = CvBridge()
        self.img = None
        self.create_subscription(Image, '/camera/color/image_raw', self.cb, 1)

    def cb(self, msg):
        try:
            self.img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass


def main():
    rclpy.init()
    node = ArucoView()
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)
    print("ArUco 实时检测 (DICT_4X4_100) —— 把标记放到相机前，ESC 退出")
    print("若画面正常但无检测: 检查标记是否太小/太暗/字典不匹配")

    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.05)
        if node.img is None:
            continue
        img = node.img.copy()
        corners, ids, _ = detector.detectMarkers(img)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            cv2.putText(img, f"detected {len(ids)}: {ids.flatten().tolist()}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            print(f"  [OK] 检测到标记 ids={ids.flatten().tolist()}")
        else:
            cv2.putText(img, "no marker (DICT_4X4_100)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("aruco view", img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
