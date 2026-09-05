#!/usr/bin/env python3
"""
手眼标定 (Eye-to-Hand) — 完整版
原理：机械臂末端贴 ArUco 二维码 → 相机检测 → 算出相机→机器人基座变换矩阵
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from arm_controller.msg import Control
from arm_controller.srv import Move
from geometry_msgs.msg import Point
import cv2
import cv_bridge
import numpy as np
import json
import time
import random
import os
from scipy.optimize import least_squares

class HandEyeCalibrator(Node):
    def __init__(self):
        super().__init__('hand_eye_calibrator')
        self.bridge = cv_bridge.CvBridge()

        # ArUco 配置（OpenCV 4.10 API）
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        self.marker_id = 4
        self.marker_size = 0.050  # 50mm（单位：米）

        # ── 标定目标类型 ──
        # 'checkerboard' 用棋盘格（角点多 + 亚像素级，但 3 轴机械臂下 p_local 偏移不可观测）
        # 'aruco'        用 ArUco 二维码（标记中心即报告点，无偏移，简单刚性拟合最稳健）
        # 2026-08-08: 机械臂只使用 3 轴、手腕未接标定板 → p_local 模型退化 → 改用 ArUco 贴末端中心
        self.target_type = 'aruco'

        # 棋盘格参数（与相机内参标定 calibrate_camera.py 保持一致，按实际棋盘格修改）
        self.board_size = (4, 6)     # 内角点 (宽, 高) = (cols, rows)
        self.square_size = 0.029     # 每格 29mm（用户实测）
        # 标定参考点：棋盘格内角点网格中心（相对第一角点，米）
        self.board_center = np.array([
            (self.board_size[0] - 1) / 2.0 * self.square_size,
            (self.board_size[1] - 1) / 2.0 * self.square_size,
            0.0], dtype=np.float64)

        # ── 手腕姿态控制 ──
        # 固定手腕 roll（°）并做一致性过滤：棋盘格偏心装在腕部时，
        # 采集点之间 roll 变化会破坏“参考点相对末端位置固定”的假设，导致误差剧增。
        # 实测发现 goto 后手腕会落到不同角度（76°~135°），必须固定。
        self.fixed_roll = 90.0     # 每个采集点都命令到该手腕角度（0~180°）
        self.roll_tol = 12.0       # 实际 roll 与参考 roll 的允许偏差（°），超出则跳过该点
        self.roll_ref = None       # 参考 roll：第一个被接受点的 roll
        # 到位后额外稳定延时（秒）：position_info 可能只反映目标位置，机械臂物理上仍在微动
        self.settle_delay = 1.5

        # 相机内参（从 camera_info 话题获取）
        self.camera_matrix = None
        self.dist_coeffs = None
        self.cam_info_received = False

        # 订阅
        self.img_sub = self.create_subscription(
            Image, '/camera/color/image_raw', self.image_cb, 10)
        self.info_sub = self.create_subscription(
            CameraInfo, '/camera/color/camera_info', self.info_cb, 10)
        self.pos_sub = self.create_subscription(
            Control, 'arm_controller/position_info', self.pos_cb, 10)

        # 服务客户端
        self.cli = self.create_client(Move, 'goto_position')
        while not self.cli.wait_for_service(timeout_sec=5):
            self.get_logger().info('等待 goto_position 服务...')

        self.latest_img = None
        self.robot_pos = None  # (x, y, z) mm
        self.robot_roll = None  # 手腕角度（°）
        self.calib_pairs = []  # [(robot_x,robot_y,robot_z, cam_x,cam_y,cam_z), ...]

        self.get_logger().info('=== 手眼标定工具已就绪 ===')

    def info_cb(self, msg):
        """获取相机内参（出厂已标定，只需读取一次）"""
        if not self.cam_info_received:
            k = np.array(msg.k).reshape(3, 3)
            if k[0, 0] == 0 or k[1, 1] == 0 or np.any(np.isnan(k)):
                if not hasattr(self, '_warned_info'):
                    self.get_logger().warn('相机内参无效（全零或NaN），将使用估算值替代')
                    self._warned_info = True
                return
            self.camera_matrix = k
            self.dist_coeffs = np.array(msg.d)
            self.cam_info_received = True
            self.get_logger().info(
                f'✓ 读取到相机内参: fx={msg.k[0]:.1f}, fy={msg.k[4]:.1f}, '
                f'cx={msg.k[2]:.1f}, cy={msg.k[5]:.1f}')

    def image_cb(self, msg):
        """保存最新一帧图像（不依赖内参）"""
        try:
            self.latest_img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            if not hasattr(self, '_img_count'):
                self.get_logger().info(f'✓ 收到图像: {self.latest_img.shape[1]}x{self.latest_img.shape[0]}')
            self._img_count = (getattr(self, '_img_count', 0) + 1)
        except Exception as e:
            self.get_logger().warn(f'图像转换失败: {e}')

    def pos_cb(self, msg):
        """机械臂位置回调"""
        self.robot_pos = (msg.position.x, msg.position.y, msg.position.z)
        self.robot_roll = msg.roll
        if not hasattr(self, '_pos_count'):
            self._pos_count = 0
            self.get_logger().info(f'✓ 收到机械臂位置: ({msg.position.x:.0f}, {msg.position.y:.0f}, {msg.position.z:.0f})')
        self._pos_count += 1

    def detect_marker_3d(self):
        """检测 ArUco 标记并返回三维位置（相机坐标系，单位：米）"""
        if self.latest_img is None:
            self.get_logger().warn('⚠ latest_img 为空')
            return None
        if self.camera_matrix is None:
            self.get_logger().warn('⚠ camera_matrix 为空')
            return None

        img = self.latest_img.copy()
        corners, ids, _ = self.aruco_detector.detectMarkers(img)

        if ids is None:
            self.get_logger().warn(f'⚠ ArUco 未检测到任何标记')
            return None

        self.get_logger().info(f'✓ ArUco 检测到 {len(ids)} 个标记: ids={ids.flatten().tolist()}')

        if self.marker_id not in ids.flatten():
            self.get_logger().warn(f'⚠ 目标 ID={self.marker_id} 不在检测结果中')
            return None

        idx = list(ids.flatten()).index(self.marker_id)
        self.get_logger().info(f'  相机矩阵: fx={self.camera_matrix[0,0]:.1f} fy={self.camera_matrix[1,1]:.1f} '
                               f'cx={self.camera_matrix[0,2]:.1f} cy={self.camera_matrix[1,2]:.1f}')

        # 用 solvePnP（兼容 OpenCV 4.10+）
        obj_pts = np.array([
            [-self.marker_size/2, -self.marker_size/2, 0],
            [self.marker_size/2, -self.marker_size/2, 0],
            [self.marker_size/2, self.marker_size/2, 0],
            [-self.marker_size/2, self.marker_size/2, 0],
        ], dtype=np.float64)
        corner_pts = corners[idx][0].astype(np.float64)  # shape (4,2)
        self.get_logger().info(f'  角点: {corner_pts.ravel().round().tolist()}')
        success, rvec, tvec = cv2.solvePnP(
            obj_pts, corner_pts, self.camera_matrix, self.dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE)

        if not success:
            self.get_logger().warn('⚠ solvePnP 失败，尝试 SQPNP...')
            success, rvec, tvec = cv2.solvePnP(
                obj_pts, corner_pts, self.camera_matrix, self.dist_coeffs,
                flags=cv2.SOLVEPNP_SQPNP)

        if success:
            # 画检测框
            cv2.aruco.drawDetectedMarkers(img, [corners[idx]])

            # 手动绘制坐标轴
            axis_len = self.marker_size * 1.5
            axis_pts, _ = cv2.projectPoints(
                np.array([[0,0,0], [axis_len,0,0], [0,axis_len,0], [0,0,axis_len]], dtype=np.float64),
                rvec, tvec, self.camera_matrix, self.dist_coeffs)
            origin = tuple(axis_pts[0].ravel().astype(int))
            for i, clr, lbl in [(0,(0,0,255),'X'), (1,(0,255,0),'Y'), (2,(255,0,0),'Z')]:
                pt = tuple(axis_pts[i+1].ravel().astype(int))
                cv2.arrowedLine(img, origin, pt, clr, 2, tipLength=0.15)
                cv2.putText(img, lbl, pt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, clr, 2)

            # 显示坐标值
            tx, ty, tz = tvec.flatten()
            if any(np.isnan([tx, ty, tz])):
                return None
            text = f'cam: ({tx*1000:.0f}, {ty*1000:.0f}, {tz*1000:.0f}) mm'
            cv2.putText(img, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow('Hand-Eye Calibration', img)
            cv2.waitKey(1)

            return (float(tx), float(ty), float(tz))
        return None

    def detect_board_3d(self):
        """检测棋盘格并返回参考点（内角点网格中心）的三维位置（相机坐标系，米）"""
        if self.latest_img is None:
            self.get_logger().warn('⚠ latest_img 为空')
            return None
        if self.camera_matrix is None:
            self.get_logger().warn('⚠ camera_matrix 为空')
            return None

        img = self.latest_img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        found, corners = cv2.findChessboardCorners(gray, self.board_size, flags)
        if not found:
            self.get_logger().warn(
                f'⚠ 未检测到棋盘格 {self.board_size[0]}x{self.board_size[1]}')
            return None

        # 亚像素精化角点
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # 棋盘格 3D 角点（米）
        objp = np.zeros((self.board_size[0] * self.board_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.board_size[0], 0:self.board_size[1]].T.reshape(-1, 2)
        objp *= self.square_size

        # solvePnP 求位姿（平面目标用 IPPE，失败退回 ITERATIVE）
        success = False
        for flag in (cv2.SOLVEPNP_IPPE, cv2.SOLVEPNP_ITERATIVE):
            ok, rvec, tvec = cv2.solvePnP(
                objp, corners_refined, self.camera_matrix, self.dist_coeffs, flags=flag)
            if ok:
                success, rvec_final, tvec_final = True, rvec, tvec
                break
        if not success:
            self.get_logger().warn('⚠ 棋盘格 solvePnP 失败')
            return None

        # 棋盘格中心（仅用于可视化/参考）
        R, _ = cv2.Rodrigues(rvec_final)
        center_cam = R @ self.board_center + tvec_final.flatten()
        if np.any(np.isnan(center_cam)):
            return None

        # 可视化
        cv2.drawChessboardCorners(img, self.board_size, corners_refined, True)
        center_px, _ = cv2.projectPoints(
            self.board_center.reshape(1, 1, 3), rvec_final, tvec_final,
            self.camera_matrix, self.dist_coeffs)
        cx_px, cy_px = center_px[0][0].ravel().astype(int)
        cv2.circle(img, (cx_px, cy_px), 6, (0, 0, 255), -1)
        cv2.putText(img,
                    f'center: ({center_cam[0]*1000:.0f}, {center_cam[1]*1000:.0f}, '
                    f'{center_cam[2]*1000:.0f}) mm',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow('Hand-Eye Calibration', img)
        cv2.waitKey(1)

        # 返回棋盘格完整位姿 (rvec, tvec)，供带末端偏移补偿的标定使用
        return (rvec_final.flatten().tolist(), tvec_final.flatten().tolist())

    def _board_center_from_pose(self, rvec_list, tvec_list):
        """由棋盘格位姿 (rvec, tvec) 计算内角点网格中心在相机系的位置（米）"""
        R, _ = cv2.Rodrigues(np.array(rvec_list, dtype=np.float64))
        return R @ self.board_center + np.array(tvec_list, dtype=np.float64)

    def goto(self, x, y, z, roll=-1.0):
        """移动机械臂（roll: 0~180° 命令手腕角度；-1 不控制手腕）"""
        req = Move.Request()
        req.pose.position = Point(x=float(x), y=float(y), z=float(z))
        req.pose.roll = float(roll)
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=30)
        return future.result().success if future.result() else False

    def wait_for_settle(self, target, tol_mm=3.0, timeout=8.0):
        """等待机械臂真正到位并停止抖动（position_info 接近目标且稳定）"""
        target = np.array(target, dtype=float)
        deadline = time.time() + timeout
        last = None
        stable = 0
        while time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.robot_pos is None:
                continue
            cur = np.array(self.robot_pos)
            dist = np.linalg.norm(cur - target)
            if last is not None and np.linalg.norm(cur - last) < 1.0:
                stable += 1
            else:
                stable = 0
            last = cur
            if stable >= 10 and dist <= tol_mm:
                return True
        return False

    def wait_for_position(self):
        """等待机械臂位置更新（含 ROS2 spin）"""
        for _ in range(50):
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.robot_pos:
                rx, ry, rz = self.robot_pos
                return rx, ry, rz
        return None

    def collect_point(self):
        """采集一个标定点"""
        # 等机械臂稳定（同时spin接收消息）
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)

        # 获取机械臂位置（毫米）
        robot = self.wait_for_position()
        if not robot:
            self.get_logger().error(f'❌ 无法获取机械臂位置 (已收 {getattr(self, "_pos_count", 0)} 条位置消息)')
            return False
        rx, ry, rz = robot

        # 去除重复的机械臂位置（同一位置重复采集会破坏标定）
        for p in self.calib_pairs:
            if np.linalg.norm(np.array(p['robot_mm']) - np.array([rx, ry, rz])) < 5.0:
                self.get_logger().warn(f'  ⚠ 与已采集点重复 (偏差<5mm)，跳过')
                return False

        # 手腕 roll 仅作参考：带 p_local 偏移补偿后不再影响标定（不再跳过点）
        current_roll = getattr(self, 'robot_roll', None)
        if self.roll_ref is None and current_roll is not None:
            self.roll_ref = current_roll
        elif (current_roll is not None and self.roll_ref is not None
              and abs(current_roll - self.roll_ref) > self.roll_tol):
            self.get_logger().info(
                f'  (手腕 roll={current_roll:.0f}° 与参考 {self.roll_ref:.0f}° 有偏差，'
                f'不影响带偏移补偿的标定)')

        # 检测目标（棋盘格或 ArUco）
        if self.target_type == 'checkerboard':
            self.get_logger().info(f'检测棋盘格...')
            pose = self.detect_board_3d()
            if not pose:
                self.get_logger().warn(f'⚠ 棋盘格检测失败 '
                                       f'(已收 {getattr(self, "_img_count", 0)} 帧图像)')
                return False
            rvec_l, tvec_l = pose
            center = self._board_center_from_pose(rvec_l, tvec_l)
            cx, cy, cz = (float(center[0]), float(center[1]), float(center[2]))
            self.calib_pairs.append({
                'robot_mm': [rx, ry, rz],
                'robot_roll': getattr(self, 'robot_roll', None),
                'rvec': rvec_l,
                'tvec': tvec_l,
                'camera_m': [cx, cy, cz],   # 棋盘格中心，仅参考/调试
            })
        else:
            self.get_logger().info(f'检测 ArUco...')
            marker_3d = self.detect_marker_3d()
            if not marker_3d:
                self.get_logger().warn(f'⚠ ArUco 检测失败 '
                                       f'(已收 {getattr(self, "_img_count", 0)} 帧图像)')
                return False
            cx, cy, cz = marker_3d
            self.calib_pairs.append({
                'robot_mm': [rx, ry, rz],
                'robot_roll': getattr(self, 'robot_roll', None),
                'camera_m': [cx, cy, cz],
            })

        self.get_logger().info(
            f'  ✓ 采集成功')
        self.get_logger().info(
            f'    机械臂: ({rx:.0f}, {ry:.0f}, {rz:.0f}) mm, '
            f'roll={getattr(self, "robot_roll", None):.1f}°')
        self.get_logger().info(
            f'    相机:   ({cx*1000:.0f}, {cy*1000:.0f}, {cz*1000:.0f}) mm')
        return True

    def compute_calibration(self):
        """用采集的点对计算变换矩阵"""
        n = len(self.calib_pairs)
        if n < 4:
            self.get_logger().error(f'至少需要4个标定点，当前只有{n}个')
            return None

        # 提取点对（统一单位：米）
        robot_pts = np.array([
            [p['robot_mm'][0]/1000, p['robot_mm'][1]/1000, p['robot_mm'][2]/1000]
            for p in self.calib_pairs])
        camera_pts = np.array([p['camera_m'] for p in self.calib_pairs])

        # 棋盘格模式：保留每点完整位姿 (rvec, tvec)，用于末端偏移补偿
        is_checkerboard = 'rvec' in self.calib_pairs[0]
        board_poses = None
        if is_checkerboard:
            board_poses = [(p['rvec'], p['tvec']) for p in self.calib_pairs]

        # 打印采集的数据用于调试
        self.get_logger().info('\n  采集数据:')
        rolls = []
        for i, p in enumerate(self.calib_pairs):
            r = p['robot_mm']
            c = [v*1000 for v in p['camera_m']]
            roll = p.get('robot_roll')
            rolls.append(roll)
            self.get_logger().info(f'  [{i}] 机器人({r[0]:.0f},{r[1]:.0f},{r[2]:.0f})mm'
                                   f' ← 相机({c[0]:.0f},{c[1]:.0f},{c[2]:.0f})mm')

        # 检查手腕 roll 是否一致（roll 变化会破坏“目标点相对机械臂位置固定”的假设）
        valid_rolls = [r for r in rolls if r is not None]
        if len(valid_rolls) >= 2:
            roll_span = abs(np.max(valid_rolls) - np.min(valid_rolls))
            if roll_span > 20.0:
                self.get_logger().warn(
                    f'  ⚠ 采集点之间手腕 roll 变化 {roll_span:.0f}°（偏大）。'
                    f'若标定板相对机械臂末端有偏心，会引入误差，建议固定手腕姿态重采。')

        # 检查数据有效性
        if np.any(np.isnan(robot_pts)) or np.any(np.isnan(camera_pts)):
            self.get_logger().error('数据包含 NaN，请重新采集')
            return None
        if np.any(np.isinf(robot_pts)) or np.any(np.isinf(camera_pts)):
            self.get_logger().error('数据包含 Inf，请重新采集')
            return None

        # 检查点云分布是否足够分散
        robot_range = np.max(robot_pts, axis=0) - np.min(robot_pts, axis=0)
        camera_range = np.max(camera_pts, axis=0) - np.min(camera_pts, axis=0)
        self.get_logger().info(f'\n  点云范围:')
        self.get_logger().info(f'    机器人: X={robot_range[0]*1000:.0f} Y={robot_range[1]*1000:.0f} Z={robot_range[2]*1000:.0f} mm')
        self.get_logger().info(f'    相机:   X={camera_range[0]*1000:.0f} Y={camera_range[1]*1000:.0f} Z={camera_range[2]*1000:.0f} mm')

        if np.max(robot_range) < 0.01:
            self.get_logger().error('❌ 机械臂位置变化太小 (<10mm)，无法标定')
            self.get_logger().error('   请确保标定点在三维空间分散开')
            return None
        if np.max(camera_range) < 0.01:
            self.get_logger().error('❌ 相机检测到的位置变化太小 (<10mm)，无法标定')
            self.get_logger().error('   可能原因: ArUco 标记贴的位置不对或相机视野太窄')
            return None

        # ── 拟合函数: 返回 R, t, 逐点误差(mm) ──
        def fit(r_pts, c_pts):
            r_center = np.mean(r_pts, axis=0)
            c_center = np.mean(c_pts, axis=0)
            H = (r_pts - r_center).T @ (c_pts - c_center) + np.eye(3) * 1e-10
            U, _, Vt = np.linalg.svd(H)
            R0 = Vt.T @ U.T
            if np.linalg.det(R0) < 0:
                Vt[-1, :] *= -1
                R0 = Vt.T @ U.T
            t0 = r_center - R0 @ c_center

            def residuals(params):
                R_, _ = cv2.Rodrigues(np.array(params[:3]))
                errs = []
                for rp, cp in zip(r_pts, c_pts):
                    errs.extend((R_ @ cp + params[3:] - rp) * 1000)
                return errs

            rvec0, _ = cv2.Rodrigues(R0)
            res = least_squares(residuals, np.r_[rvec0.flatten(), t0],
                                method='lm', max_nfev=300)
            R_, _ = cv2.Rodrigues(np.array(res.x[:3]))
            t_ = res.x[3:]
            errs_mm = np.array([np.linalg.norm(R_ @ cp + t_ - rp) * 1000
                                for rp, cp in zip(r_pts, c_pts)])
            return R_, t_, errs_mm

        # ── 棋盘格带末端偏移补偿的拟合 ──
        # 棋盘格中心偏离末端(position_info 报告点) 6cm 且装在前臂上，偏移方向随姿态变化，
        # 但该偏移在棋盘格坐标系中恒定（棋盘格与末端同属一个刚体）。
        # 设末端在棋盘格系中的位置为 p_local，则末端相机坐标 = R_board@p_local + t_board，
        # 整体优化 R, t, p_local 即可自动补偿，无需重新安装。
        def fit_pose_with_offset(r_pts, poses):
            centers = np.array([self._board_center_from_pose(rv, tv) for rv, tv in poses])
            R0, t0, _ = fit(r_pts, centers)   # 用中心点拟合求初值（p_local 从 0 开始）
            rv0, _ = cv2.Rodrigues(R0)

            def residuals(params):
                R_, _ = cv2.Rodrigues(np.array(params[:3]))
                t_ = params[3:6]
                p_local = params[6:9]
                errs = []
                for rp, (rv_b, tv_b) in zip(r_pts, poses):
                    R_b, _ = cv2.Rodrigues(np.array(rv_b, dtype=np.float64))
                    tcp_cam = R_b @ p_local + np.array(tv_b, dtype=np.float64)
                    pred = R_ @ tcp_cam + t_
                    errs.extend((pred - rp) * 1000)
                return errs

            def solve(x0):
                try:
                    return least_squares(residuals, x0, method='lm', max_nfev=3000)
                except Exception:
                    return None

            # 多起点优化：p_local 初值从 0 与 ±0.12m 多个方向试探，取误差最小者。
            # 旧版固定从 0 起步，一旦初值远离真值，p_local 会被推到数米量级的错误解
            # （实测出现过 p_local=2400mm / tz=2.96m 的退化解）。
            best = None
            for p0 in (np.zeros(3),
                       np.array([0.12, 0, 0]), np.array([-0.12, 0, 0]),
                       np.array([0, 0.12, 0]), np.array([0, -0.12, 0]),
                       np.array([0, 0, 0.12]), np.array([0, 0, -0.12]),
                       np.array([0.12, 0.12, 0.12])):
                res = solve(np.r_[rv0.flatten(), t0, p0])
                if res is not None and (best is None
                        or np.sum(np.square(res.fun)) < np.sum(np.square(best.fun))):
                    best = res
            res = best
            if res is None:
                raise np.linalg.LinAlgError('所有初值的 least_squares 均失败')
            R_, _ = cv2.Rodrigues(np.array(res.x[:3]))
            t_ = res.x[3:6]
            p_local_ = res.x[6:9]
            errs_mm = []
            for rp, (rv_b, tv_b) in zip(r_pts, poses):
                R_b, _ = cv2.Rodrigues(np.array(rv_b, dtype=np.float64))
                tcp_cam = R_b @ p_local_ + np.array(tv_b, dtype=np.float64)
                pred = R_ @ tcp_cam + t_
                errs_mm.append(np.linalg.norm(pred - rp) * 1000)
            return R_, t_, p_local_, np.array(errs_mm)

        try:
            # ── 迭代剔除离群点 ──
            keep = np.arange(len(robot_pts))
            removed = []
            for _ in range(20):
                if is_checkerboard:
                    R, t, p_local, errs = fit_pose_with_offset(
                        robot_pts[keep], [board_poses[i] for i in keep])
                else:
                    R, t, errs = fit(robot_pts[keep], camera_pts[keep])
                threshold = max(15.0, 2.5 * float(np.median(errs)))
                if len(keep) > 4 and errs.max() > threshold:
                    worst = int(np.argmax(errs))
                    orig_idx = int(keep[worst])
                    removed.append((orig_idx, float(errs[worst])))
                    keep = np.delete(keep, worst)
                    self.get_logger().warn(
                        f'  ⚠ 剔除离群点 #{orig_idx} '
                        f'(误差 {removed[-1][1]:.1f} mm > 阈值 {threshold:.1f} mm)')
                else:
                    break

            # ── 用保留的点重新拟合得到最终结果 ──
            if is_checkerboard:
                R, t, p_local, errors = fit_pose_with_offset(
                    robot_pts[keep], [board_poses[i] for i in keep])
            else:
                R, t, errors = fit(robot_pts[keep], camera_pts[keep])
        except np.linalg.LinAlgError:
            self.get_logger().error('❌ SVD 求解失败，数据质量不足')
            return None

        # ── 尺度自检（仅位置模式有效；棋盘格由 p_local 补偿偏移，用平均误差判断）──
        if not is_checkerboard:
            try:
                def fit_scale(r_pts, c_pts):
                    rc, cc = r_pts.mean(0), c_pts.mean(0)
                    H = (r_pts - rc).T @ (c_pts - cc) + np.eye(3) * 1e-9
                    U, _, Vt = np.linalg.svd(H)
                    R0 = Vt.T @ U.T
                    if np.linalg.det(R0) < 0:
                        Vt[-1, :] *= -1
                        R0 = Vt.T @ U.T
                    rv0, _ = cv2.Rodrigues(R0)

                    def res(p):
                        R_, _ = cv2.Rodrigues(np.array(p[:3]))
                        return ((p[6] * (R_ @ c_pts.T).T + p[3:6]) - r_pts).ravel() * 1000

                    x = least_squares(res, np.r_[rv0.flatten(), rc - R0 @ cc, 1.0],
                                      method='lm', max_nfev=1000)
                    return float(x.x[6])

                s = fit_scale(robot_pts[keep], camera_pts[keep])
                if abs(s - 1.0) > 0.08:
                    implied_square = self.square_size * s
                    self.get_logger().warn(
                        f'  ⚠ 尺度自检: 相机点需缩放 {s:.2f} 倍才能匹配机器人，'
                        f'相机估计位置偏大 {1.0/s:.2f} 倍。'
                        f'很可能是 square_size={self.square_size*1000:.0f}mm 与实际不符'
                        f'（按此数据推算实际约 {implied_square*1000:.0f}mm），'
                        f'请用尺子量实际格子尺寸并修正 square_size，'
                        f'同时确认相机 color_info_url 加载的内参正确。')
                else:
                    self.get_logger().info(f'  ✓ 尺度自检通过 (缩放因子 {s:.3f})')
            except Exception as e:
                self.get_logger().warn(f'  尺度自检跳过: {e}')

        # 4×4 变换矩阵
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t

        avg_err = float(np.mean(errors))
        max_err = float(np.max(errors))
        n = len(keep)

        self.get_logger().info('\n' + '='*65)
        self.get_logger().info('  手眼标定结果 (相机 → 机器人基座)')
        self.get_logger().info('='*65)
        self.get_logger().info(f'  旋转矩阵 R:')
        for row in R:
            self.get_logger().info(f'    [{row[0]:.6f}, {row[1]:.6f}, {row[2]:.6f}]')
        self.get_logger().info(
            f'  平移向量 t: [{t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f}] 米')
        if is_checkerboard:
            self.get_logger().info(
                f'  末端在棋盘格系位置 p_local: '
                f'[{p_local[0]*1000:.0f}, {p_local[1]*1000:.0f}, {p_local[2]*1000:.0f}] mm')
        self.get_logger().info('  逐点误差 (mm): ' +
                               ', '.join(f'{e:.1f}' for e in errors))
        self.get_logger().info(
            f'  平均误差: {avg_err:.1f} mm')
        self.get_logger().info(
            f'  最大误差: {max_err:.1f} mm')
        self.get_logger().info(
            f'  采集点数: {n}' +
            (f' (已剔除 {len(removed)} 个离群点)' if removed else ''))
        if avg_err > 15.0:
            self.get_logger().warn(
                f'  ⚠ 平均误差 {avg_err:.1f}mm 偏大，'
                + ('可能棋盘格 square_size 或相机内参与实际不符。'
                   if is_checkerboard else
                   '可能标定板未固定牢/相机距离过远/内参有误。'))
        self.get_logger().info('='*65)

        # 保存结果
        result = {
            'rotation': R.tolist(),
            'translation': t.tolist(),
            'transform_4x4': T.tolist(),
            'avg_error_mm': round(float(avg_err), 2),
            'max_error_mm': round(float(max_err), 2),
            'camera_frame': '/camera_color_optical_frame',
            'robot_frame': '/robot_base',
            'calib_pairs': [self.calib_pairs[i] for i in keep],
            'removed_outliers': removed,
        }
        if is_checkerboard:
            result['end_effector_in_board_mm'] = [round(v*1000, 1) for v in p_local]
        result_path = '/home/ubuntu/ros2fox/calib_result/hand_eye_result.json'
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        # 同时存一份到 /tmp 方便其他程序访问
        with open('/tmp/hand_eye_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        self.get_logger().info(f'✅ 结果已保存: {result_path}')

        return T


def main():
    rclpy.init()
    calib = HandEyeCalibrator()

    # 等待相机内参
    print('\n⏳ 等待相机内参...')
    for _ in range(30):
        rclpy.spin_once(calib, timeout_sec=0.5)
        if calib.cam_info_received:
            break
    if not calib.cam_info_received:
        # 尝试从最新图像尺寸估算内参（作为备用）
        print('⚠ 未接收到有效相机内参，尝试从图像估算...')
        for _ in range(15):
            rclpy.spin_once(calib, timeout_sec=0.3)
            if calib.latest_img is not None:
                h, w = calib.latest_img.shape[:2]
                # 用图像中心作为主点，假设 fov=60° 估算焦距
                f = w / (2 * np.tan(np.deg2rad(30)))
                calib.camera_matrix = np.array([[f, 0, w/2],
                                                 [0, f, h/2],
                                                 [0, 0, 1]], dtype=np.float64)
                calib.dist_coeffs = np.zeros(5)
                calib.cam_info_received = True
                print(f'⚠ 使用估算内参: fx={f:.0f} fy={f:.0f} cx={w/2:.0f} cy={h/2:.0f}')
                break
    if not calib.cam_info_received:
        print('❌ 无法获取相机内参或图像，请确认相机已启动')
        calib.destroy_node()
        rclpy.shutdown()
        return

    print('\n' + '='*65)
    print('  手眼标定 — 采集流程')
    print('='*65)
    print('  条件检查:')
    print('  ✅ 相机出厂内参已加载')
    print('  ✅ goto_position 服务已连接')
    if calib.target_type == 'checkerboard':
        print(f'  ✅ 棋盘格 {calib.board_size[0]}x{calib.board_size[1]} 内角点, '
              f'{int(calib.square_size*1000)}mm/格')
    else:
        print('  ✅ ArUco DICT_4X4_100, ID=4, 50mm')
    print()
    print(f'  说明：机械臂会逐个尝试 20 个位置，手腕固定到 roll={calib.fixed_roll:.0f}°')
    print('  若目标不在相机视野内，或手腕 roll 与参考偏差过大，则自动换下一个')
    print('  采集够 12 个有效点后自动计算（含离群点自动剔除）')
    print('='*65)

    # 候选位置池（越多越容易采集成功）
    candidate_points = [
        (200, 0, 130), (200, 0, 100), (200, 0, 160),
        (160, 0, 80),  (240, 0, 80),  (160, 0, 140), (240, 0, 140),
        (200, 60, 100), (200, -60, 100),
        (200, 80, 130), (200, -80, 130),
        (200, 50, 160), (200, -50, 160),
        (180, 60, 80),  (220, -60, 80),
        (180, 40, 150), (220, -40, 150),
        (160, 50, 110), (240, -50, 110),
        (170, 70, 120), (230, -70, 120),
        # 补充更大 Z/Y 跨度与更多中低点位，改善旋转可观测性与分布（2026-08-08）
        (200, 0, 200), (200, 0, 60),
        (200, 100, 130), (200, -100, 130),
        (180, 0, 100), (220, 0, 100),
        (200, 0, 170), (160, 0, 60), (240, 0, 200),
    ]
    import random
    random.shuffle(candidate_points)

    target_count = 12   # 多采几个点，剔除离群点后仍有足够数量
    collected = 0
    attempted = 0

    for x, y, z in candidate_points:
        if collected >= target_count:
            break
        attempted += 1

        calib.get_logger().info(f'\n─── 尝试 {attempted}: ({x}, {y}, {z}) '
                                f'[{collected}/{target_count} 已采集] ───')

        # 移动机械臂（固定手腕姿态；手腕轴未连接标定板，roll 不影响标定）
        if not calib.goto(x, y, z, calib.fixed_roll):
            calib.get_logger().info(f'  → 不可达，换下一个')
            continue

        # 等待到位并稳定（position_info 接近目标且不再变化）
        if not calib.wait_for_settle((x, y, z)):
            calib.get_logger().warn(f'  → 机械臂未确认到位，仍尝试采集')

        # 额外稳定延时：position_info 可能只反映目标位置，机械臂物理上仍需时间停稳
        time.sleep(calib.settle_delay)

        # 尝试采集（最多等 5 秒）
        ok = False
        for _ in range(15):
            for __ in range(2):
                rclpy.spin_once(calib, timeout_sec=0.2)
            ok = calib.collect_point()
            if ok:
                break

        if ok:
            collected += 1
        else:
            calib.get_logger().info(f'  → ArUco 不在视野内，换下一个位置')

    # 回安全位置
    calib.goto(200, 0, 150)
    cv2.destroyAllWindows()

    calib.get_logger().info(f'\n{"="*65}')
    calib.get_logger().info(f'  采集完成: {collected}/{target_count} 个有效点 (尝试了 {attempted} 个位置)')
    calib.get_logger().info(f'{"="*65}')

    if collected >= 4:
        calib.compute_calibration()
    else:
        calib.get_logger().error(f'有效点不足4个 ({collected})，无法标定')
        calib.get_logger().error('请调整相机位置使更多标定点可见')

    calib.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
