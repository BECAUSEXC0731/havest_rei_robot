#!/usr/bin/env python3
"""
用尺子直接实测相机焦距 fx —— 独立于任何标定结果的真值检验

原理：
  把已知 29mm 的棋盘格正对相机放在距离 D 米处，
  检测相邻内角点的像素间距 px，则
      fx ≈ px × D / 0.029

用法：
  python3 measure_fx.py <D>
     D: 从相机镜头前表面到棋盘格的距离（米），用卷尺量
  例：
  python3 measure_fx.py 0.5

  启动后把棋盘格正对相机（尽量垂直于光轴），
  画面出现角点时脚本会连续打印 fx 估计值，取稳定平均。
"""
import sys
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

BOARD = (4, 6)     # 内角点
SQUARE = 0.029     # 29mm


class FXMeasure(Node):
    def __init__(self):
        super().__init__('measure_fx')
        self.bridge = CvBridge()
        self.img = None
        self.create_subscription(Image, '/camera/color/image_raw', self.cb, 1)

    def cb(self, msg):
        try:
            self.img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass


def main():
    if len(sys.argv) < 2:
        print("用法: python3 measure_fx.py <距离D米>  例: python3 measure_fx.py 0.5")
        sys.exit(1)
    D = float(sys.argv[1])
    if D <= 0:
        print("距离需 > 0")
        sys.exit(1)

    rclpy.init()
    node = FXMeasure()
    print(f"棋盘格 {BOARD[0]}x{BOARD[1]} 内角点, 每格 {SQUARE*1000:.0f}mm, 距离 D={D:.3f} m")
    print("请把棋盘格正对相机（垂直于光轴），观察打印的 fx 值……")
    print("Ctrl+C 退出")

    vals = []
    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.05)
        if node.img is None:
            continue
        img = node.img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        found, corners = cv2.findChessboardCorners(gray, BOARD, flags)
        if not found:
            cv2.putText(img, "no board", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 255), 2)
            cv2.imshow("measure fx", img)
            cv2.waitKey(1)
            continue

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        pts = corners.reshape(BOARD[1], BOARD[0], 2)   # rows=6, cols=4

        # 相邻内角点像素间距（水平、垂直）
        h = []
        for r in range(BOARD[1]):
            for c in range(BOARD[0] - 1):
                h.append(np.linalg.norm(pts[r, c + 1] - pts[r, c]))
        v = []
        for c in range(BOARD[0]):
            for r in range(BOARD[1] - 1):
                v.append(np.linalg.norm(pts[r + 1, c] - pts[r, c]))
        px_h = float(np.mean(h))
        px_v = float(np.mean(v))

        fx_h = px_h * D / SQUARE
        fx_v = px_v * D / SQUARE
        fx = (fx_h + fx_v) / 2.0
        vals.append(fx)

        cv2.drawChessboardCorners(img, BOARD, corners, True)
        txt = f"fx~{fx:.0f}  (h={fx_h:.0f} v={fx_v:.0f})  avg={np.mean(vals[-20:]):.0f}"
        cv2.putText(img, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("measure fx", img)
        cv2.waitKey(1)

        if len(vals) % 10 == 0:
            print(f"  fx 估计 ≈ {np.mean(vals[-20:]):.0f}  (最近20帧平均)")

    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
