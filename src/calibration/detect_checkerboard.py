#!/usr/bin/env python3
"""
棋盘格检测诊断工具
启动相机后，运行此脚本，它会自动检测棋盘格并显示检测到的尺寸
"""

import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# 常见棋盘格内角点组合，按可能性排序
PATTERN_CANDIDATES = [
    (4, 6),   # 5x7 格子
    (5, 7),   # 6x8 格子
    (7, 5),   # 8x6 格子 (宽7高5内角点)
    (6, 4),   # 7x5 格子
    (8, 6),   # 9x7 格子 (标准大棋盘)
    (6, 8),   # 7x9 格子
    (9, 6),   # 10x7 格子
    (6, 9),   # 7x10 格子
    (4, 11),  # 5x12 格子 (细长)
    (11, 4),  # 12x5 格子
]

class CheckerboardDetector(Node):
    def __init__(self, topic='/camera/color/image_raw'):
        super().__init__('checkerboard_detector')
        self.bridge = CvBridge()
        self.latest = None
        self.sub = self.create_subscription(Image, topic, self.callback, 1)

    def callback(self, msg):
        try:
            raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if raw.dtype == np.uint16 and len(raw.shape) == 2:
                gray = cv2.normalize(raw, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            elif len(raw.shape) == 3:
                gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
            else:
                gray = raw
            self.latest = (raw, gray)
        except Exception as e:
            self.get_logger().warn(f"Error: {e}")

def main():
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else '/camera/color/image_raw'

    rclpy.init()
    node = CheckerboardDetector(topic)

    print("=" * 60)
    print(f"棋盘格检测诊断工具")
    print(f"话题: {topic}")
    print("请在画面中展示棋盘格，脚本会自动检测")
    print("按 ESC 退出")
    print("=" * 60)

    cv2.namedWindow("Checkerboard Detector")
    detected = False

    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.05)

        if node.latest is None:
            canvas = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(canvas, "Waiting for camera...", (140, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.imshow("Checkerboard Detector", canvas)
            if cv2.waitKey(30) & 0xFF == 27:
                break
            continue

        raw, gray = node.latest
        h, w = gray.shape

        # 自适应直方图均衡化增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 转为彩色显示
        display = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        detected = False
        best_match = None
        best_corners = None

        for pattern in PATTERN_CANDIDATES:
            found, corners = cv2.findChessboardCorners(enhanced, pattern, None)
            if found:
                detected = True
                best_match = pattern
                best_corners = corners
                break

        if detected:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            refined = cv2.cornerSubPix(gray, best_corners, (11, 11), (-1, -1), criteria)
            cv2.drawChessboardCorners(display, best_match, refined, True)

            cols, rows = best_match
            msg = f"DETECTED! Inner corners: {cols}x{rows} (Grid: {cols+1}x{rows+1} squares, 30mm)"
            cv2.putText(display, msg, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(display, f"Calibration cmd: --size {cols}x{rows} --square 0.030",
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)
        else:
            cv2.putText(display, "No chessboard detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(display, "Trying patterns:", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            y = 75
            for p in PATTERN_CANDIDATES:
                cv2.putText(display, f"  {p[0]}x{p[1]} corners  ({p[0]+1}x{p[1]+1} squares)",
                            (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
                y += 18

            # 显示图像信息
            info = f"Size: {w}x{h}  Depth: {gray.dtype}"
            cv2.putText(display, info, (10, display.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        cv2.imshow("Checkerboard Detector", display)
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
