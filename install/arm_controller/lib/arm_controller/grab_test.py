#!/usr/bin/env python3
"""
手眼标定验证 — 检测 ArUco → 转换坐标 → 机械臂去抓取
用法：
  1. 把 ArUco 标定板从机械臂取下，放在桌面任意位置
  2. 运行此脚本
  3. 机械臂自动移动到标定板位置
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from arm_controller.srv import Move
from geometry_msgs.msg import Point
import cv2
import cv_bridge
import numpy as np
import json
import os

class GrabTest(Node):
    def __init__(self):
        super().__init__('grab_test')
        self.bridge = cv_bridge.CvBridge()

        # 加载标定结果
        calib_paths = [
            '/home/ubuntu/ros2fox/calib_result/hand_eye_result.json',
            '/tmp/hand_eye_result.json'
        ]
        calib_data = None
        for p in calib_paths:
            if os.path.exists(p):
                with open(p) as f:
                    calib_data = json.load(f)
                self.get_logger().info(f'✓ 加载标定结果: {p}')
                break
        if not calib_data:
            self.get_logger().error('❌ 未找到标定结果，请先运行 hand_eye_calib.py')
            raise FileNotFoundError('标定文件未找到')

        self.T = np.array(calib_data['transform_4x4'])  # 相机→机器人基座

        # ArUco 配置
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        self.marker_id = 4
        self.marker_size = 0.050  # 50mm

        # 等待相机内参和图像
        self.camera_matrix = None
        self.dist_coeffs = None
        self.latest_img = None

        self.info_sub = self.create_subscription(
            CameraInfo, '/camera/color/camera_info', self.info_cb, 10)
        self.img_sub = self.create_subscription(
            Image, '/camera/color/image_raw', self.image_cb, 10)

        # 等待服务
        self.cli = self.create_client(Move, 'goto_position')
        while not self.cli.wait_for_service(timeout_sec=5):
            self.get_logger().info('等待 goto_position 服务...')

        self.get_logger().info('=== 抓取测试已就绪 ===')

    def info_cb(self, msg):
        if self.camera_matrix is not None:
            return
        k = np.array(msg.k).reshape(3, 3)
        if k[0, 0] == 0 or np.any(np.isnan(k)):
            return
        self.camera_matrix = k
        self.dist_coeffs = np.array(msg.d)
        self.get_logger().info(f'✓ 相机内参已加载')

    def image_cb(self, msg):
        try:
            self.latest_img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass

    def detect_marker(self):
        """检测 ArUco，返回在相机坐标系下的 3D 位置（米）"""
        if self.latest_img is None or self.camera_matrix is None:
            return None, None

        img = self.latest_img.copy()
        corners, ids, _ = self.aruco_detector.detectMarkers(img)

        if ids is None or self.marker_id not in ids.flatten():
            return None, None

        idx = list(ids.flatten()).index(self.marker_id)
        corner_pts = corners[idx][0].astype(np.float64)

        # 解算位姿
        obj_pts = np.array([[-0.025,-0.025,0],[0.025,-0.025,0],[0.025,0.025,0],[-0.025,0.025,0]], dtype=np.float64)
        success, rvec, tvec = cv2.solvePnP(obj_pts, corner_pts, self.camera_matrix, self.dist_coeffs, flags=cv2.SOLVEPNP_IPPE)

        if not success:
            return None, None

        # 画检测结果
        cv2.aruco.drawDetectedMarkers(img, [corners[idx]])
        t = tvec.flatten()
        text = f'cam: ({t[0]*1000:.0f}, {t[1]*1000:.0f}, {t[2]*1000:.0f}) mm'
        cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # 转换到机器人坐标
        marker_cam = np.array([t[0], t[1], t[2], 1.0])
        marker_robot = self.T @ marker_cam
        text2 = f'robot: ({marker_robot[0]*1000:.0f}, {marker_robot[1]*1000:.0f}, {marker_robot[2]*1000:.0f}) mm'
        cv2.putText(img, text2, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        cv2.imshow('Grab Test', img)
        cv2.waitKey(1)

        return t, marker_robot[:3]

    def goto(self, x, y, z):
        """移动机械臂"""
        req = Move.Request()
        req.pose.position = Point(x=float(x), y=float(y), z=float(z))
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=15)
        return future.result().success if future.result() else False


def main():
    rclpy.init()
    test = GrabTest()

    # 等待内参
    for _ in range(30):
        rclpy.spin_once(test, timeout_sec=0.5)
        if test.camera_matrix is not None:
            break
    if test.camera_matrix is None:
        print('❌ 未收到相机内参')
        test.destroy_node()
        rclpy.shutdown()
        return

    print('\n' + '='*60)
    print('  手眼标定验证 — 抓取测试')
    print('='*60)
    print('  请将 ArUco 标定板 (ID=4) 放在相机视野内的桌面上')
    print('  按 Enter 开始检测...')
    input()

    # 检测 ArUco
    for _ in range(50):
        rclpy.spin_once(test, timeout_sec=0.2)
        cam_pos, robot_pos = test.detect_marker()
        if robot_pos is not None:
            break

    if robot_pos is None:
        print('❌ 未检测到 ArUco 标定板')
        test.destroy_node()
        rclpy.shutdown()
        return

    rx, ry, rz = robot_pos * 1000  # 转毫米
    print(f'\n✅ 检测到标定板（机械臂未移动）')
    print(f'  相机坐标: ({cam_pos[0]*1000:.0f}, {cam_pos[1]*1000:.0f}, {cam_pos[2]*1000:.0f}) mm')
    print(f'  机器人坐标: ({rx:.0f}, {ry:.0f}, {rz:.0f}) mm')
    print()

    # 用户确认后才开始移动
    ans = input('  是否让机械臂移动到该位置？(y/n): ').strip().lower()
    if ans != 'y':
        print('  已取消')
        test.destroy_node()
        rclpy.shutdown()
        return

    # 先到安全高度
    safe_z = max(rz, 100)
    print(f'\n→ 移动到安全高度 (rx, ry, {safe_z:.0f})...')
    success = test.goto(rx, ry, safe_z)
    if not success:
        print(f'  ⚠ 安全位置不可达，已取消')
        test.destroy_node()
        rclpy.shutdown()
        return

    ans = input(f'\n  当前位置: ({rx:.0f}, {ry:.0f}, {safe_z:.0f})\n  按 Enter 让机械臂下降到目标高度 ({rz:.0f}mm)...').strip()

    # 下降到目标
    print(f'→ 下降到目标 ({rx:.0f}, {ry:.0f}, {rz:.0f})...')
    success = test.goto(rx, ry, rz)
    if success:
        print(f'✅ 到达目标位置！')
    else:
        print(f'⚠ 目标不可达')

    test.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
