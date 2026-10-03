"""地图数据：解析 map_server 的 YAML + PGM，供前端 Canvas 画底图。

为什么要后端解析而不是前端直接读 PGM：
* 前端拿不到文件系统；把 PGM 转成 PNG 后浏览器 <img>/canvas 直接可用，体积也小；
* `origin` / `resolution` 必须由后端与图像一起给出，前端才能做世界↔像素换算。

坐标约定（重要）
----------------
PGM 第 0 行对应地图 y 最大处（图像 y 向下），所以：
    像素 col = (x - origin_x) / resolution
    像素 row = height - (y - origin_y) / resolution
前端必须按这个公式画，否则机器人会上下镜像。

栅格语义（ROS map_server 约定，受 YAML 的 negate/occupied_thresh/free_thresh 影响）：
    occupied → 深色(20)   free → 浅色(220)   unknown → 中灰(110)
"""
from __future__ import annotations

import os
import threading
import time

import cv2
import numpy as np
import yaml

DEFAULT_MAP_YAML = '/home/ubuntu/ros2fox/maps/test_map.yaml'

# 显示用灰度（深色主题下也能看清墙与通道）
GRAY_OCCUPIED = 20
GRAY_UNKNOWN = 110
GRAY_FREE = 220


class MapData:
    """地图加载与缓存（按文件 mtime 自动失效）。"""

    def __init__(self, yaml_path: str = DEFAULT_MAP_YAML):
        self.yaml_path = yaml_path
        self._lock = threading.Lock()
        self._cache = None          # (meta dict, png bytes)
        self._stamp = 0.0

    # ── 内部：加载 ──
    def _load(self):
        with open(self.yaml_path, 'r') as f:
            cfg = yaml.safe_load(f)

        image_name = cfg.get('image', '')
        if not os.path.isabs(image_name):
            image_name = os.path.join(os.path.dirname(self.yaml_path), image_name)
        img = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f'地图图像读不到: {image_name}')
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        negate = int(cfg.get('negate', 0))
        occ_th = float(cfg.get('occupied_thresh', 0.65))
        free_th = float(cfg.get('free_thresh', 0.196))

        norm = img.astype(np.float32) / 255.0
        occ = (1.0 - norm) if negate else norm           # 1=占据
        out = np.full(img.shape, GRAY_UNKNOWN, np.uint8)
        out[occ > occ_th] = GRAY_OCCUPIED
        out[occ < free_th] = GRAY_FREE

        ok, png = cv2.imencode('.png', out)
        if not ok:
            raise RuntimeError('地图 PNG 编码失败')

        origin = cfg.get('origin', [0.0, 0.0, 0.0])
        meta = {
            'ok': True,
            'yaml': self.yaml_path,
            'image': image_name,
            'width': int(out.shape[1]),
            'height': int(out.shape[0]),
            'resolution': float(cfg.get('resolution', 0.05)),
            'origin': [float(origin[0]), float(origin[1]),
                       float(origin[2]) if len(origin) > 2 else 0.0],
            'negate': negate,
            'occupied_thresh': occ_th,
            'free_thresh': free_th,
            'image_url': '/api/map.png',
            'frame': 'map',
        }
        return meta, png.tobytes()

    # ── 对外 ──
    def get(self):
        """返回 (meta, png_bytes)，带 mtime 缓存。"""
        try:
            stamp = os.path.getmtime(self.yaml_path)
            img_stamp = 0.0
            with open(self.yaml_path) as f:
                _name = (yaml.safe_load(f) or {}).get('image', '')
            if _name:
                p = _name if os.path.isabs(_name) else os.path.join(
                    os.path.dirname(self.yaml_path), _name)
                img_stamp = os.path.getmtime(p)
            stamp = max(stamp, img_stamp)
        except Exception:
            stamp = time.time()

        with self._lock:
            if self._cache is None or stamp != self._stamp:
                self._cache = self._load()
                self._stamp = stamp
            return self._cache

    def meta(self) -> dict:
        try:
            return self.get()[0]
        except Exception as exc:
            return {'ok': False, 'error': repr(exc), 'yaml': self.yaml_path}

    def png(self) -> bytes | None:
        try:
            return self.get()[1]
        except Exception:
            return None
