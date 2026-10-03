#!/usr/bin/env python3
"""
彩色 ↔ IR(深度) 外参标定 —— 手动深度对齐的准备工作

原理：
  棋盘格同时被彩色相机和 IR(深度)相机看到，
  分别 solvePnP 得到棋盘格在彩色系、IR 系的位姿，
  两者相减得到 T_color_to_ir（彩色→IR 的 4×4 变换）。

前置：
  1. 相机以 彩色 + IR 双流启动（launch 里 enable_color/enable_ir 都为 true）
  2. 棋盘格放在两个相机都能看到的位置（你的棋盘格需在 IR 图里也能被检测到）

用法：
  python3 src/calibration/calibrate_color_ir.py

  按 空格 采集一组（两窗口都显示绿色角点连线时按）
  采集 15~20 组不同角度/位置后按 q 保存
  结果: calib_result/color_ir_extrinsic.json

按键：
  空格  采集一组   r 重置   q/ESC 结束并保存
"""
import json
import os
import numpy as np
import cv2
import yaml
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

# ── 棋盘格参数（必须和你实际棋盘格一致！）──
BOARD_SIZE = (4, 6)    # 内角点 (宽, 高) = (cols, rows)
SQUARE_SIZE = 0.029    # 每格 29mm（用户实测）

ROOT = '/home/ubuntu/ros2fox'
COLOR_INFO = os.path.join(ROOT, 'calib_data', 'color', 'color_camera_info.yaml')
IR_INFO = os.path.join(ROOT, 'calib_data', 'ir', 'ir_camera_info.yaml')
OUT_PATH = os.path.join(ROOT, 'calib_result', 'color_ir_extrinsic.json')


def load_camera_info(path):
    with open(path) as f:
        d = yaml.safe_load(f)
    K = np.array(d['camera_matrix']['data'], dtype=np.float64).reshape(3, 3)
    dist = np.array(d['distortion_coefficients']['data'], dtype=np.float64)
    return K, dist


def solve_board_pose(gray, K, dist):
    """检测棋盘格并返回位姿 (rvec, tvec, 精化角点)；失败返回 (None,None,None)"""
    if gray.dtype != np.uint8:
        # IR 是 uint16，OpenCV 棋盘格检测只支持 8bit → 归一化到 8bit
        if gray.size == 0 or float(gray.max()) <= 0:
            return None, None, None
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
    found, corners = cv2.findChessboardCorners(gray, BOARD_SIZE, flags)
    if not found:
        return None, None, None
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

    objp = np.zeros((BOARD_SIZE[0] * BOARD_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:BOARD_SIZE[0], 0:BOARD_SIZE[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    ok = False
    for flag in (cv2.SOLVEPNP_IPPE, cv2.SOLVEPNP_ITERATIVE):
        ok, rvec, tvec = cv2.solvePnP(objp, corners, K, dist, flags=flag)
        if ok:
            break
    if not ok:
        return None, None, None
    return rvec, tvec, corners


class ColorIRExtrinsic(Node):
    def __init__(self):
        super().__init__('color_ir_extrinsic')
        self.bridge = CvBridge()
        # 彩色内参：优先从相机 topic 读（保证和相机实际发布、抓取链路一致）
        # IR 内参：用标定文件（相机 IR topic 固件返回 NaN）
        self.K_c = None
        self.d_c = np.zeros(5)
        self.K_i, self.d_i = load_camera_info(IR_INFO)
        self.latest_color = None
        self.latest_ir = None
        self.T_list = []   # 每组求得的 彩色→IR 4×4

        self.create_subscription(Image, '/camera/color/image_raw',
                                 self.color_cb, qos_profile_sensor_data)
        self.create_subscription(CameraInfo, '/camera/color/camera_info',
                                 self.info_cb, 1)
        self.create_subscription(Image, '/camera/ir/image_raw',
                                 self.ir_cb, qos_profile_sensor_data)

        self.get_logger().info(f"IR 内参 fx={self.K_i[0,0]:.1f}")
        self.get_logger().info("等待彩色 camera_info（将使用相机实际发布的内参）...")
        self.get_logger().info("把棋盘格放到彩色+IR 都能看到的位置，按 空格 采集，q 保存")

    def info_cb(self, msg):
        if self.K_c is None:
            k = np.array(msg.k).reshape(3, 3)
            if k[0, 0] > 100 and not np.any(np.isnan(k)):
                self.K_c = k
                self.d_c = np.array(msg.d)
                self.get_logger().info(f"彩色内参(来自相机topic) fx={k[0,0]:.1f} cx={k[0,2]:.1f}")

    def color_cb(self, msg):
        try:
            self.latest_color = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass

    def ir_cb(self, msg):
        try:
            img = self.bridge.imgmsg_to_cv2(msg, 'passthrough')
            if img.ndim == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.latest_ir = img
        except Exception:
            pass

    def capture(self):
        """在最新彩色+IR 上同时检测棋盘格，求一组 T_color_to_ir"""
        if self.latest_color is None or self.latest_ir is None or self.K_c is None:
            return None
        cgray = cv2.cvtColor(self.latest_color, cv2.COLOR_BGR2GRAY)
        rc, tc, _ = solve_board_pose(cgray, self.K_c, self.d_c)
        ri, ti, _ = solve_board_pose(self.latest_ir, self.K_i, self.d_i)
        if rc is None or ri is None:
            return None

        Rc, _ = cv2.Rodrigues(rc); tc = tc.flatten()
        Ri, _ = cv2.Rodrigues(ri); ti = ti.flatten()
        T_bc = np.eye(4); T_bc[:3, :3] = Rc; T_bc[:3, 3] = tc   # 棋盘→彩色
        T_bi = np.eye(4); T_bi[:3, :3] = Ri; T_bi[:3, 3] = ti   # 棋盘→IR
        # 彩色→IR = 棋盘到IR × (棋盘到彩色)^{-1}
        return T_bi @ np.linalg.inv(T_bc)

    def _normalize_mono16(self, img, clip_max=4000):
        """把 uint16 的 IR 图归一化到 0-255 用于显示"""
        valid = img > 0
        display = np.zeros_like(img, dtype=np.uint8)
        if np.any(valid):
            v = img[valid]
            lo = float(np.min(v))
            hi = min(float(np.max(v)), clip_max)
            if hi > lo:
                scaled = np.clip(img, lo, hi).astype(np.float32)
                display = ((scaled - lo) / (hi - lo) * 255).astype(np.uint8)
        return display

    def _preview(self):
        """实时预览彩色+IR，标注棋盘格检测状态；没图时提示等待话题"""
        h = 480
        if self.latest_color is not None and self.K_c is not None:
            disp_c = self.latest_color.copy()
            rc, _, cc = solve_board_pose(cv2.cvtColor(disp_c, cv2.COLOR_BGR2GRAY),
                                         self.K_c, self.d_c)
            if rc is not None:
                cv2.drawChessboardCorners(disp_c, BOARD_SIZE, cc, True)
                cv2.putText(disp_c, 'COLOR: OK', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(disp_c, 'COLOR: no board', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('COLOR', disp_c)
        else:
            blank = np.zeros((h, 640, 3), dtype=np.uint8)
            txt = ('waiting /camera/color/image_raw ...' if self.latest_color is None
                   else 'waiting color camera_info ...')
            cv2.putText(blank, txt, (30, h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('COLOR', blank)

        if self.latest_ir is not None:
            disp_i = cv2.cvtColor(self._normalize_mono16(self.latest_ir),
                                  cv2.COLOR_GRAY2BGR)
            ri, _, ci = solve_board_pose(self.latest_ir, self.K_i, self.d_i)
            if ri is not None:
                cv2.drawChessboardCorners(disp_i, BOARD_SIZE, ci, True)
                cv2.putText(disp_i, 'IR: OK', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(disp_i, 'IR: no board', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('IR', disp_i)
        else:
            blank = np.zeros((h, 640, 3), dtype=np.uint8)
            cv2.putText(blank, 'waiting /camera/ir/image_raw ...', (30, h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('IR', blank)

    def save(self):
        if len(self.T_list) == 0:
            self.get_logger().error("没有采集到数据，未保存")
            return
        Rs = np.array([T[:3, :3] for T in self.T_list])
        ts = np.array([T[:3, 3] for T in self.T_list])
        # 旋转取平均(投影到SO(3))，平移取平均
        R_avg, _ = cv2.Rodrigues(np.array([cv2.Rodrigues(R)[0] for R in Rs]).mean(0))
        t_avg = ts.mean(0)
        T = np.eye(4); T[:3, :3] = R_avg; T[:3, 3] = t_avg

        result = {
            'T_color_to_ir_4x4': T.tolist(),
            'rotation': R_avg.tolist(),
            'translation': t_avg.tolist(),
            'color_frame': '/camera_color_optical_frame',
            'ir_frame': '/camera_ir_optical_frame',
            'pairs': len(self.T_list),
        }
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, 'w') as f:
            json.dump(result, f, indent=2)
        print("\n" + "=" * 55)
        print("  彩色 → IR 外参标定结果")
        print("=" * 55)
        print(f"  平移 t(mm): [{t_avg[0]*1000:.1f}, {t_avg[1]*1000:.1f}, {t_avg[2]*1000:.1f}]")
        print(f"  采集组数: {len(self.T_list)}")
        print(f"  已保存: {OUT_PATH}")
        print("=" * 55)

    def run(self):
        cv2.namedWindow('COLOR')
        cv2.namedWindow('IR')
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
            self._preview()
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q'), ord('Q')):
                break
            elif key == ord('r'):
                self.T_list = []
                self.get_logger().info("已重置")
            elif key == ord(' '):
                T = self.capture()
                if T is None:
                    self.get_logger().warn("彩色/IR 未同时检测到棋盘格，未采集")
                else:
                    self.T_list.append(T)
                    t = T[:3, 3]
                    self.get_logger().info(
                        f"采集 {len(self.T_list)} 组, t(mm)=["
                        f"{t[0]*1000:.0f}, {t[1]*1000:.0f}, {t[2]*1000:.0f}]")
        cv2.destroyAllWindows()
        self.save()


def main():
    rclpy.init()
    node = ColorIRExtrinsic()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
