#!/usr/bin/env python3
"""
葡萄检测独立测试脚本
用于在不启动完整工作流的情况下测试 YOLO 检测 + 深度图 3D 定位。

用法:
  # 实时检测（需要相机数据）
  ros2 run fox_grape_harvest test_detection.py

  # 指定模型和配置
  ros2 run fox_grape_harvest test_detection.py \
    --model /path/to/grape.pt \
    --config /path/to/harvest_config.yaml
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import numpy as np
import cv2
import argparse
import os
import sys
from collections import deque

# 将上级目录加入 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fox_grape_harvest.yolo_detector import YoloDetector
from fox_grape_harvest.depth_utils import (
    load_hand_eye_calibration, depth_to_robot_3d_stable,
    load_d2c_config, depth_to_robot_3d_d2c_stable,
    depth_to_robot_3d_nearest_in_box,
    get_depth_at_pixel
)


class DetectionTestNode(Node):
    """YOLO 检测 + 深度定位测试节点。"""

    def __init__(self, model_path: str, calib_path: str, conf: float = 0.5):
        super().__init__('grape_detection_test')

        self.bridge = CvBridge()
        self.latest_rgb = None
        self.latest_depth = None
        self.depth_history = deque(maxlen=7)   # 最近几帧深度，取中值抗闪烁
        self.camera_matrix = None
        self.cam_info_received = False
        self._depth_logged = False
        self._display_warned = False

        # 可抓取性(工作空间)参数：从 harvest_config.yaml 读取
        self.arm_ws = self._load_arm_workspace()

        # 手眼标定
        self.T_cam_to_robot = load_hand_eye_calibration(calib_path)

        # 手动深度对齐配置 (彩色↔IR)
        self.d2c = load_d2c_config(
            '/home/ubuntu/ros2fox/calib_result/color_ir_extrinsic.json',
            '/home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml')
        if self.d2c is not None:
            self.K_ir, self.T_color_to_ir = self.d2c
            self.get_logger().info("✅ 已加载手动深度对齐配置 (D2C)")
        else:
            self.K_ir = None
            self.T_color_to_ir = None
            self.get_logger().warn("⚠ 未加载手动对齐配置，按未对齐处理")

        # YOLO
        if os.path.exists(model_path):
            self.detector = YoloDetector(model_path, conf)
            self.get_logger().info(f"✅ YOLO: {model_path}")
        else:
            self.get_logger().error(f"❌ 模型不存在: {model_path}")
            self.detector = None

        # 订阅
        self.create_subscription(
            Image, '/camera/color/image_raw', self._rgb_cb, qos_profile_sensor_data)
        self.create_subscription(
            Image, '/camera/depth/image_raw',
            self._depth_cb, qos_profile_sensor_data)
        self.create_subscription(
            CameraInfo, '/camera/color/camera_info', self._info_cb, 1)

        self.get_logger().info("检测测试已启动，按 Ctrl+C 退出")

    def _info_cb(self, msg):
        if self.cam_info_received:
            return
        k = np.array(msg.k).reshape(3, 3)
        if k[0, 0] == 0 or np.any(np.isnan(k)):
            return
        self.camera_matrix = k
        self.cam_info_received = True
        self.get_logger().info(f"相机内参: fx={k[0,0]:.1f}, fy={k[1,1]:.1f}")

    def _rgb_cb(self, msg):
        try:
            self.latest_rgb = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass

    def _depth_cb(self, msg):
        try:
            depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if depth.dtype == np.uint16:
                # 本相机深度话题单位是 厘米(cmV)！/100 转米（实测 50cm 表面显示 50）
                depth = depth.astype(np.float32) / 100.0
            elif depth.dtype == np.float32:
                pass  # 已经是米
            self.latest_depth = depth
            self.depth_history.append(depth)
            if not self._depth_logged:
                self._depth_logged = True
                valid = depth[(depth >= 0.1) & (depth <= 3.0)]
                self.get_logger().info(
                    f"深度帧: shape={depth.shape} min={depth.min():.3f}m "
                    f"max={depth.max():.3f}m 有效(0.1~3m)={len(valid)}/{depth.size} "
                    f"零值={np.count_nonzero(depth == 0)}")
        except Exception as e:
            self.get_logger().warn(f"深度转换失败: {e}")

    def _probe_no_depth(self, cx: int, cy: int, depth: np.ndarray) -> str:
        """诊断无深度原因：报告彩色像素与 D2C 映射的 IR 像素处的原始深度。"""
        try:
            d_c = get_depth_at_pixel(depth, cx, cy)
            parts = [f"彩色像素({cx},{cy})深度={d_c * 1000:.0f}mm" if d_c
                     else f"彩色像素({cx},{cy})深度=无效"]
            if self.T_color_to_ir is not None and self.K_ir is not None:
                fx_c, fy_c = self.camera_matrix[0, 0], self.camera_matrix[1, 1]
                cx_c, cy_c = self.camera_matrix[0, 2], self.camera_matrix[1, 2]
                fx_i, fy_i = self.K_ir[0, 0], self.K_ir[1, 1]
                cx_i, cy_i = self.K_ir[0, 2], self.K_ir[1, 2]
                R = self.T_color_to_ir[:3, :3]
                t = self.T_color_to_ir[:3, 3]
                d = 0.5
                u_i, v_i = cx, cy
                for _ in range(4):
                    P_c = d * np.array([(cx - cx_c) / fx_c, (cy - cy_c) / fy_c, 1.0])
                    P_i = R @ P_c + t
                    if P_i[2] <= 0:
                        break
                    u_i = int(round(fx_i * P_i[0] / P_i[2] + cx_i))
                    v_i = int(round(fy_i * P_i[1] / P_i[2] + cy_i))
                    d_i = get_depth_at_pixel(depth, u_i, v_i)
                    if d_i is None or d_i <= 0:
                        break
                    if abs(d_i - d) < 0.003:
                        break
                    d = d_i
                d_i = get_depth_at_pixel(depth, u_i, v_i)
                parts.append(f"IR像素({u_i},{v_i})深度={d_i * 1000:.0f}mm" if d_i
                             else f"IR像素({u_i},{v_i})深度=无效")
            return " | ".join(parts)
        except Exception as e:
            return f"诊断异常: {e}"

    def _safe_show(self, img):
        """安全显示窗口；无显示环境时提示而不是崩溃/黑屏。"""
        try:
            cv2.imshow('Grape Detection Test', img)
            cv2.waitKey(1)
        except Exception as e:
            if not self._display_warned:
                self._display_warned = True
                self.get_logger().warn(f"无法创建显示窗口(检查 DISPLAY): {e}")

    def _load_arm_workspace(self):
        """读取 harvest_config.yaml 的机械臂工作空间参数（可抓取性判断用）。"""
        import yaml
        default = {
            'ws_x_min': 30, 'ws_x_max': 320,
            'ws_y_min': -180, 'ws_y_max': 180,
            'ws_z_min': 20, 'ws_z_max': 200,
            'margin': 20,
        }
        cfg_path = '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml'
        try:
            with open(cfg_path) as f:
                arm_cfg = yaml.safe_load(f).get('arm', {}) or {}
            key_map = {
                'ws_x_min': 'workspace_x_min', 'ws_x_max': 'workspace_x_max',
                'ws_y_min': 'workspace_y_min', 'ws_y_max': 'workspace_y_max',
                'ws_z_min': 'workspace_z_min', 'ws_z_max': 'workspace_z_max',
            }
            for k, ck in key_map.items():
                if ck in arm_cfg:
                    default[k] = arm_cfg[ck]
            self.get_logger().info(
                f"工作空间: X[{default['ws_x_min']},{default['ws_x_max']}] "
                f"Y[{default['ws_y_min']},{default['ws_y_max']}] "
                f"Z[{default['ws_z_min']},{default['ws_z_max']}]mm "
                f"(裕度 {default['margin']}mm)")
        except Exception:
            self.get_logger().warn("未读取到工作空间配置，使用默认值")
        return default

    def _graspability(self, x, y, z):
        """判断目标点是否可抓取（在机械臂工作空间内）。
        返回 (可抓取, 短码): GRASP 或 NO:X/Y/Z（哪些轴超界）。
        """
        ws = self.arm_ws
        m = ws['margin']

        def in_r(v, lo, hi):
            return (lo + m) <= v <= (hi - m)

        in_x = in_r(x, ws['ws_x_min'], ws['ws_x_max'])
        in_y = in_r(y, ws['ws_y_min'], ws['ws_y_max'])
        in_z = in_r(z, ws['ws_z_min'], ws['ws_z_max'])
        if in_x and in_y and in_z:
            return True, "GRASP"
        bad = []
        if not in_x:
            bad.append('X')
        if not in_y:
            bad.append('Y')
        if not in_z:
            bad.append('Z')
        return False, "NO:" + ''.join(bad)

    def run_once(self):
        """执行一次检测并显示结果。"""
        # 数据未就绪时也显示窗口，标注缺什么（排查"看不到图"用）
        if (self.latest_rgb is None or self.latest_depth is None
                or self.camera_matrix is None or self.detector is None):
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            missing = []
            if self.latest_rgb is None:
                missing.append('无彩色 /camera/color/image_raw')
            if self.latest_depth is None:
                missing.append('无深度 /camera/depth/image_raw')
            if self.camera_matrix is None:
                missing.append('无内参 camera_info')
            if self.detector is None:
                missing.append('模型未加载')
            txt = '等待: ' + ' | '.join(missing) if missing else '等待数据...'
            cv2.putText(img, txt, (30, 240), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)
            self.get_logger().warn(f"⏳ {txt}")
            self._safe_show(img)
            return

        rgb = self.latest_rgb.copy()
        depth = self.latest_depth.copy()

        # 检测
        detections = self.detector.detect(rgb)
        img = self.detector.draw_detections(rgb, detections)

        # 3D 定位 + 可抓取性
        graspable_cnt = 0
        for det in detections:
            cx, cy = det['center']
            frames = list(self.depth_history) if self.depth_history else [depth]
            if self.T_color_to_ir is not None:
                # 优先：检测框内找最近有效深度点（深色葡萄中心像素常无深度）
                pt_mm, d_m = depth_to_robot_3d_nearest_in_box(
                    det['bbox'], frames, self.camera_matrix, self.K_ir,
                    self.T_color_to_ir, self.T_cam_to_robot)
            else:
                pt_mm, d_m = depth_to_robot_3d_stable(
                    cx, cy, frames, self.camera_matrix, self.T_cam_to_robot)
            if pt_mm is not None:
                x, y, z = pt_mm
                graspable, gcode = self._graspability(x, y, z)
                if graspable:
                    graspable_cnt += 1
                color = (0, 255, 0) if graspable else (0, 0, 255)
                label = f"({x:.0f},{y:.0f},{z:.0f}) {gcode} d={d_m*1000:.0f}"
                cv2.putText(img, label, (cx - 90, cy + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            else:
                # 深度无效：提示为什么没有坐标
                cv2.putText(img, "no depth", (cx - 60, cy + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)
                self.get_logger().warn(
                    f"像素({cx},{cy}) 无深度 → {self._probe_no_depth(cx, cy, depth)}")

        # 显示信息
        cv2.putText(img,
                    f"Detected: {len(detections)}  Graspable: {graspable_cnt}/{len(detections)}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        self._safe_show(img)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='/home/ubuntu/ros2fox/models/grape.pt')
    parser.add_argument('--calib', default='/home/ubuntu/ros2fox/calib_result/hand_eye_result.json')
    parser.add_argument('--conf', type=float, default=0.5)
    args = parser.parse_args()

    rclpy.init()
    node = DetectionTestNode(args.model, args.calib, args.conf)

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            node.run_once()
            # 按 q 退出
            try:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
