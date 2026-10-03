#!/usr/bin/env python3
"""
生成可打印的棋盘格标定板 (PNG/PDF)

用法:
  python3 generate_checkerboard.py                    # 生成 8x6 格子, 边长 30mm
  python3 generate_checkerboard.py --cols 9 --rows 7 --square 25 --units mm

参数:
  --cols     棋盘格宽方向内角点数 (默认 8)
  --rows     棋盘格高方向内角点数 (默认 6)
  --square   每个格子的边长, 单位 mm (默认 30)
  --output   输出文件名 (默认 checkerboard_8x6_30mm.png)
"""

import argparse
import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='生成棋盘格标定板')
    parser.add_argument('--cols', type=int, default=8, help='内角点数 (宽)')
    parser.add_argument('--rows', type=int, default=6, help='内角点数 (高)')
    parser.add_argument('--square', type=float, default=30, help='格子边长 (mm)')
    parser.add_argument('--dpi', type=int, default=300, help='输出 DPI')
    parser.add_argument('--output', default=None, help='输出文件名')
    args = parser.parse_args()

    cols = args.cols      # 内角点数
    rows = args.rows      # 内角点数
    square_mm = args.square
    dpi = args.dpi

    # 物理尺寸
    board_width_px = (cols + 1) * square_mm / 25.4 * dpi   # 格子数 = 内角数 + 1
    board_height_px = (rows + 1) * square_mm / 25.4 * dpi

    board_width_px = int(round(board_width_px))
    board_height_px = int(round(board_height_px))

    # 绘制棋盘格
    chessboard = np.zeros((board_height_px, board_width_px), dtype=np.uint8)
    square_px = int(round(square_mm / 25.4 * dpi))

    for i in range(rows + 1):
        for j in range(cols + 1):
            if (i + j) % 2 == 0:
                y1 = i * square_px
                y2 = (i + 1) * square_px
                x1 = j * square_px
                x2 = (j + 1) * square_px
                chessboard[y1:y2, x1:x2] = 255

    # 添加边框和标注
    margin = 80  # px
    canvas_h = board_height_px + 2 * margin
    canvas_w = board_width_px + 2 * margin
    canvas = np.ones((canvas_h, canvas_w), dtype=np.uint8) * 255
    canvas[margin:margin + board_height_px, margin:margin + board_width_px] = chessboard

    # 标注信息
    label = f"Checkerboard: {cols}x{rows} corners, {square_mm:.0f}mm square"
    cv2.putText(canvas, label,
                (margin, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
    calib_cmd = f"ros2 run camera_calibration cameracalibrator --size {cols}x{rows} --square {square_mm/1000:.3f}"
    cv2.putText(canvas, f"Calibration cmd: {calib_cmd}",
                (margin, canvas_h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 128, 1)

    # 保存
    if args.output is None:
        filename = f"checkerboard_{cols}x{rows}_{int(square_mm)}mm.png"
    else:
        filename = args.output

    cv2.imwrite(filename, canvas)
    print(f"[OK] 棋盘格已保存: {filename}")
    print(f"     尺寸: {cols+1}x{rows+1} 格, 每格 {square_mm:.0f}mm")
    print(f"     内角点: {cols}x{rows}")
    print(f"     打印时请确保缩放比例为 100%")
    print(f"")
    print(f"标定命令 (ROS2):")
    print(f"  ros2 run camera_calibration cameracalibrator \\")
    print(f"    --size {cols}x{rows} --square {square_mm/1000:.3f} \\")
    print(f"    --ros-args -r /image:=/camera/color/image_raw")
    print(f"                      -r /camera_info:=/camera/color/camera_info")
    print(f"")
    print(f"标定 IR 相机:")
    print(f"  ros2 run camera_calibration cameracalibrator \\")
    print(f"    --size {cols}x{rows} --square {square_mm/1000:.3f} \\")
    print(f"    --ros-args -r /image:=/camera/ir/image_raw")
    print(f"                      -r /camera_info:=/camera/ir/camera_info")


if __name__ == '__main__':
    main()
