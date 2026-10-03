"""3Hz 实时识别预览（"摄像头的实时识别"）。

为什么需要它
------------
现有 `/grape_harvest/debug_image` **只在采摘流程运行时**才发布，平时看不到识别效果；
而"看着屏幕判断该不该抓"恰恰是 WebUI 最常用的功能。

实现原则：**复用，不重写**
--------------------------
YOLO、深度→相机3D、手动 D2C、手眼矩阵、可抓性判定全部 `import`
`fox_grape_harvest` 的现成实现（`yolo_detector` / `depth_utils`）。
一旦在 WebUI 里抄第二份，将来标定/参数一改就会两边不一致。

按需运行
--------
检测很吃 CPU/GPU（彩色+深度 30Hz 反序列化 + YOLO 推理），所以**引用计数**：
只有 `/video/detect` 有观看者、或前端轮询 `/api/detections` 时才真正订阅+推理。

两种模式
--------
* `yolo`：真实检测（需要 `models/grape.pt` 训练可用）
* `sim` ：在画面中心造一个假框，但**深度/D2C/手眼/可抓性全部走真实代码** ——
          用于没有训练模型/没有葡萄时自检整条坐标链路
"""
from __future__ import annotations

import math
import os
import threading
import time
from collections import deque

import cv2
import numpy as np
import yaml

from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image

# ── 复用 fox_grape_harvest 的实现（绝不重写）──
from fox_grape_harvest.yolo_detector import YoloDetector
from fox_grape_harvest.depth_utils import (
    load_hand_eye_calibration, load_d2c_config, load_grasp_check, classify_reach,
    depth_to_robot_3d_nearest_in_box, GRASP, MARGINAL, UNREACHABLE,
)

DEFAULT_CONFIG = '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml'

REACH_COLOR = {GRASP: (80, 220, 80), MARGINAL: (0, 190, 255), UNREACHABLE: (60, 60, 230)}
REACH_NAME = {GRASP: '可抓', MARGINAL: '临界', UNREACHABLE: '不可达'}


class PreviewDetector:
    """3Hz 检测循环（线程）+ 结果缓存（线程安全）。"""

    DEPTH_HISTORY = 3          # 多帧中值用的深度帧数（原 5；实测采样开销太高，3 帧足够）

    def __init__(self, node, store, config_path: str = DEFAULT_CONFIG,
                 mode: str = 'yolo', hz: float = 3.0,
                 color_topic: str = '/camera/color/image_raw',
                 depth_topic: str = '/camera/depth/image_raw',
                 info_topic: str = '/camera/color/camera_info'):
        self.node = node
        self.store = store
        self.cfg_path = config_path
        self.mode = mode
        self.hz = max(0.5, float(hz))
        self.color_topic = color_topic
        self.depth_topic = depth_topic
        self.info_topic = info_topic

        self.bridge = CvBridge()
        self._lock = threading.Lock()
        self._refs = 0
        self._slots = []
        self._subs = []
        self._thread = None
        self._running = False

        self._rgb = None
        self._depth_frames = deque(maxlen=self.DEPTH_HISTORY)
        self._K_color = None
        self._detections: list[dict] = []
        self._annotated = None
        self._last_error = ''
        self._last_run = 0.0
        self._fps_measured = 0.0
        self._warned_K = False
        self._last_rgb_conv = 0.0
        self._last_depth_conv = 0.0

        # ── 加载配置与标定（YOLO 模型延迟到首次启用时才加载，避免拖慢启动）──
        self.cfg = self._load_config()
        self.detector = None
        self._yolo_tried = False
        self._init_calib()

    # ══════════ 配置与标定 ══════════

    def _load_config(self) -> dict:
        for p in (self.cfg_path,
                  '/home/ubuntu/ros2fox/install/fox_grape_harvest/share/fox_grape_harvest/config/harvest_config.yaml'):
            if p and os.path.exists(p):
                try:
                    with open(p) as f:
                        return yaml.safe_load(f) or {}
                except Exception:
                    continue
        self.node.get_logger().warn(f'[preview] 读不到配置: {self.cfg_path}')
        return {}

    def _init_yolo(self):
        path = self.cfg.get('yolo_model_path', '')
        if not path or not os.path.exists(path):
            self.node.get_logger().warn(
                f'[preview] YOLO 模型不存在({path}) → 自动切到 sim 模式（只自检坐标链路）')
            self.mode = 'sim'
            return
        try:
            self.detector = YoloDetector(path, self.cfg.get('yolo_confidence', 0.5),
                                         self.cfg.get('target_class', 'grape'))
            self.node.get_logger().info(f'[preview] YOLO 已加载: {path}')
        except Exception as exc:
            self.node.get_logger().error(f'[preview] YOLO 加载失败({exc}) → 切到 sim 模式')
            self.mode = 'sim'

    def _init_calib(self):
        self.T_cam_to_robot = load_hand_eye_calibration(
            self.cfg.get('hand_eye_calib_path',
                         '/home/ubuntu/ros2fox/calib_result/hand_eye_result.json'))
        d2c = load_d2c_config(
            self.cfg.get('d2c_extrinsic_path',
                         '/home/ubuntu/ros2fox/calib_result/color_ir_extrinsic.json'),
            self.cfg.get('ir_camera_info_path',
                         '/home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml'))
        if d2c is None:
            self.K_ir, self.T_color_to_ir = None, None
            self.node.get_logger().warn('[preview] 未找到 D2C 标定 → 深度按未对齐处理')
        else:
            self.K_ir, self.T_color_to_ir = d2c

        arm = self.cfg.get('arm', {}) or {}
        self.ws = {
            'x_min': arm.get('workspace_x_min', 30), 'x_max': arm.get('workspace_x_max', 335),
            'y_min': arm.get('workspace_y_min', -190), 'y_max': arm.get('workspace_y_max', 190),
            'z_min': arm.get('workspace_z_min', 20), 'z_max': arm.get('workspace_z_max', 220),
        }
        self.gc = load_grasp_check(self.cfg)

    # ══════════ 引用计数式启停 ══════════

    @property
    def active(self) -> bool:
        return self._running

    def acquire(self, slot=None) -> None:
        """占用一个启用名额（**任意线程可调，不碰 rclpy 实体**）。

        真正的订阅/退订由 VideoBroker 的 2Hz timer 在 executor 线程里调用
        start_now()/stop_now() —— 否则从 asyncio 线程 create/destroy subscription
        会与正在 spin 的 executor 死锁（实测踩过，见 video.py 注释）。
        """
        with self._lock:
            self._refs += 1
            if slot is not None and slot not in self._slots:
                self._slots.append(slot)

    def release(self, slot=None) -> None:
        """释放名额（任意线程可调，不碰 rclpy 实体）。"""
        with self._lock:
            self._refs = max(0, self._refs - 1)
            if slot is not None and slot in self._slots:
                self._slots.remove(slot)

    @property
    def want_active(self) -> bool:
        """期望状态：还有人在用（供 executor 线程比对）。"""
        with self._lock:
            return self._refs > 0

    def start_now(self):
        """真正启动订阅+检测线程。**只允许在 executor 线程（ROS timer）里调用**。"""
        if self._running:
            return
        if self.mode == 'yolo' and not self._yolo_tried:
            self._yolo_tried = True
            self._init_yolo()          # 首次启用才导入 ultralytics/加载模型
        self._subs.append(self.node.create_subscription(
            Image, self.color_topic, self._on_rgb, qos_profile_sensor_data))
        self._subs.append(self.node.create_subscription(
            Image, self.depth_topic, self._on_depth, qos_profile_sensor_data))
        self._subs.append(self.node.create_subscription(
            CameraInfo, self.info_topic, self._on_info, qos_profile_sensor_data))
        # ⚠️ camera_info 必须用 sensor QoS（BEST_EFFORT）：
        #    相机（含 Orbbec 真机）用 BEST_EFFORT 发布，订阅端若用 RELIABLE
        #    两者 QoS 不兼容 → 永远收不到内参 → 深度/手眼链路静默失效（实测踩过）
        self._running = True
        self._thread = threading.Thread(target=self._loop, name='preview-detector', daemon=True)
        self._thread.start()
        self.node.get_logger().info(
            f'[preview] 识别已启用 (mode={self.mode}, {self.hz:.1f}Hz)')

    def stop_now(self):
        """停订阅+停检测线程。**只允许在 executor 线程（ROS timer）里调用**。"""
        self._running = False
        for sub in self._subs:
            try:
                self.node.destroy_subscription(sub)
            except Exception:
                pass
        self._subs = []
        self._rgb = None
        self._depth_frames.clear()
        with self._lock:
            self._detections = []
        self.node.get_logger().info('[preview] 识别已停用（无观看者）')

    # ══════════ 相机回调 ══════════

    def _on_info(self, msg: CameraInfo):
        if self._K_color is not None:
            return
        k = np.array(msg.k).reshape(3, 3)
        if k[0, 0] > 0:
            self._K_color = k
            self.node.get_logger().info(
                f'[preview] 彩色内参 fx={k[0,0]:.1f} fy={k[1,1]:.1f}')

    def _on_rgb(self, msg: Image):
        # 丢帧降频：源可能 30Hz，而检测只跑 hz 次/秒 ——
        # 必须在 cv_bridge 之前丢弃，否则每次回调都做 921KB 拷贝（实测会把后端拖到 70% CPU）
        now = time.time()
        if now - self._last_rgb_conv < 1.0 / self.hz:
            return
        self._last_rgb_conv = now
        try:
            self._rgb = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass

    def _on_depth(self, msg: Image):
        now = time.time()
        if now - self._last_depth_conv < 1.0 / self.hz:
            return
        self._last_depth_conv = now
        try:
            raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception:
            return
        if raw.dtype == np.uint16:
            d = raw.astype(np.float32) / 100.0      # ⚠️ 本相机深度单位是 cm
        elif raw.dtype == np.float32:
            d = raw
        else:
            return
        self._depth_frames.append(d)

    # ══════════ 检测主循环 ══════════

    def _loop(self):
        period = 1.0 / self.hz
        while self._running:
            t0 = time.time()
            try:
                self._tick()
            except Exception as exc:
                self._last_error = repr(exc)
                self.node.get_logger().warn(f'[preview] 检测异常: {exc}')
            dt = time.time() - t0
            self._last_run = time.time()
            self._fps_measured = 1.0 / max(dt, 1e-3) if dt > 0 else 0.0
            time.sleep(max(0.0, period - dt))

    def _tick(self):
        rgb = self._rgb
        if rgb is None:
            return
        depths = list(self._depth_frames)
        if self.K_color is None and not self._warned_K:
            self._warned_K = True
            self.node.get_logger().warn(
                '[preview] 未收到 camera_info → 无法做像素→3D（检查相机是否带正确内参启动）')

        boxes = self._detect(rgb)
        results = []
        for i, (bbox, conf, cls_name) in enumerate(boxes):
            item = {'id': i, 'cls': cls_name, 'conf': round(float(conf), 3),
                    'bbox': [int(v) for v in bbox], 'depth_m': None,
                    'robot_mm': None, 'reach': UNREACHABLE, 'reach_code': 'NO_DATA'}
            if depths and self.K_ir is not None and self.K_color is not None:
                pt_mm, depth_m = depth_to_robot_3d_nearest_in_box(
                    bbox, depths, self.K_color, self.K_ir,
                    self.T_color_to_ir, self.T_cam_to_robot, step=8)
                if pt_mm is not None:
                    x, y, z = float(pt_mm[0]), float(pt_mm[1]), float(pt_mm[2])
                    level, code = classify_reach(x, y, z, self.ws, self.gc)
                    item.update({'robot_mm': [round(x, 1), round(y, 1), round(z, 1)],
                                 'depth_m': round(float(depth_m), 3),
                                 'reach': int(level), 'reach_code': code})
            results.append(item)

        annotated = self._annotate(rgb, results)
        with self._lock:
            self._detections = results
            self._annotated = annotated
        for slot in list(self._slots):
            slot.set(annotated)

    def _detect(self, rgb):
        """返回 [(bbox, conf, class_name), ...]"""
        if self.mode == 'sim':
            h, w = rgb.shape[:2]
            size = 90
            cx, cy = w // 2, h // 2
            bbox = [cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2]
            return [(bbox, 0.99, 'sim-grape')]
        if self.detector is None:
            return []
        raw = self.detector.detect(rgb) or []
        out = []
        for d in raw:
            try:
                out.append((d['bbox'], d.get('confidence', 0.0), d.get('class_name', '?')))
            except Exception:
                continue
        return out

    def _annotate(self, rgb, results):
        img = rgb.copy()
        for it in results:
            x1, y1, x2, y2 = it['bbox']
            color = REACH_COLOR.get(it['reach'], (200, 200, 200))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            lines = [f"{it['cls']} {it['conf']:.2f}"]
            if it['robot_mm']:
                x, y, z = it['robot_mm']
                lines.append(f'X{x:.0f} Y{y:.0f} Z{z:.0f} mm')
                lines.append(f"d={it['depth_m']:.2f}m {REACH_NAME.get(it['reach'], '?')}"
                             f" ({it['reach_code']})")
            else:
                lines.append('no depth')
            for k, text in enumerate(lines):
                cv2.putText(img, text, (x1, max(14, y1 - 8 - 14 * (len(lines) - 1 - k))),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

        cv2.putText(img, f"preview {self.mode} {self.hz:.0f}Hz "
                         f"dets={len(results)}", (8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        if self._last_error:
            cv2.putText(img, f'err: {self._last_error[:60]}', (8, img.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 230), 1, cv2.LINE_AA)
        return img

    # ══════════ 对外结果 ══════════

    def snapshot(self) -> list:
        with self._lock:
            return list(self._detections)

    def status(self) -> dict:
        return {
            'active': self._running,
            'mode': self.mode,
            'hz': self.hz,
            'refs': self._refs,
            'detections': len(self.snapshot()),
            'has_rgb': self._rgb is not None,
            'has_depth': len(self._depth_frames) > 0,
            'has_K': self.K_color is not None,
            'error': self._last_error,
        }

    @property
    def K_color(self):
        return self._K_color
