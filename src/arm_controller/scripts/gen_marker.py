#!/usr/bin/env python3
"""生成 ArUco 标定板 (4x4, ID=4, 50mm)"""
import cv2
import numpy as np
import os

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
marker = cv2.aruco.generateImageMarker(aruco_dict, 4, 500)

out_path = '/tmp/aruco_marker_4.png'
cv2.imwrite(out_path, marker)
print(f'✅ 标定板已生成: {out_path}')
print(f'   尺寸: 500×500 像素 (打印时请缩放到 50mm×50mm)')
print(f'   ArUco 字典: DICT_4X4_100, ID=4')
print()
print('请用 50mm×50mm 打印此图片，贴在机械臂末端吸盘上。')
