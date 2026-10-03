#!/usr/bin/env python3
"""
depth_viewer.py
深度图与红外图可视化工具 - 鼠标悬停显示像素值

启动:
  ros2 run grape_detect depth_viewer.py

话题:
  /camera/depth/image_raw - 深度图 (16UC1, cm 厘米!)
  /camera/ir/image_raw    - 红外图 (MONO16)
  /camera/color/image_raw - RGB 图 (可选)

按键:
  ESC / q  - 退出
  s        - 保存当前截图到文件
  1/2/3    - 切换布局: 1=深度+红外, 2=深度+RGB, 3=三图同显
"""

import sys
import cv2
import rclpy
import numpy as np
from collections import deque
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class DepthViewer(Node):
    def __init__(self):
        super().__init__('depth_viewer')

        self.bridge = CvBridge()
        self.layout_mode = 1  # 1=深度+红外, 2=深度+RGB, 3=三图同显

        # 图像缓存
        self.depth_img = None
        self.ir_img = None
        self.rgb_img = None

        # 多帧深度缓存：时间中值(多帧取中位数)稳定葡萄这类闪烁深度
        self.depth_history = deque(maxlen=7)
        self.temporal_smooth = False  # 't' 键切换

        # 订阅话题
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth/image_raw', self.depth_callback, 1)
        self.ir_sub = self.create_subscription(
            Image, '/camera/ir/image_raw', self.ir_callback, 1)
        self.rgb_sub = self.create_subscription(
            Image, '/camera/color/image_raw', self.rgb_callback, 1)

        # 鼠标位置
        self.mouse_x = -1
        self.mouse_y = -1

        self.get_logger().info("=" * 50)
        self.get_logger().info("深度/红外/RGB 可视化工具已启动")
        self.get_logger().info("按键: ESC/q=退出  s=截图  1=深度+IR  2=深度+RGB  3=三图同显")
        self.get_logger().info("=" * 50)

    def depth_callback(self, msg):
        depth_data = np.frombuffer(msg.data, dtype=np.uint16)
        self.depth_img = depth_data.reshape(msg.height, msg.width)
        self.depth_history.append(self.depth_img.copy())
        self.depth_width = msg.width
        self.depth_height = msg.height

    def ir_callback(self, msg):
        ir_data = np.frombuffer(msg.data, dtype=np.uint16)
        self.ir_img = ir_data.reshape(msg.height, msg.width)

    def rgb_callback(self, msg):
        rgb_data = np.frombuffer(msg.data, dtype=np.uint8)
        # 驱动发布 RGB8，cv2.imshow 需要 BGR → 反转通道，否则红蓝互换颜色不对
        self.rgb_img = rgb_data.reshape(msg.height, msg.width, 3)[:, :, ::-1]

    def mouse_callback(self, event, x, y, flags, param):
        self.mouse_x = x
        self.mouse_y = y

    def _normalize_mono16(self, img, clip_max=5000):
        """将 MONO16 图归一化到 0-255 用于显示"""
        valid = img > 0
        display = np.zeros_like(img, dtype=np.uint8)
        if np.any(valid):
            min_v = np.min(img[valid])
            max_v = np.max(img[valid])
            cmin = max(min_v, 0)
            cmax = min(max_v, clip_max)
            if cmax > cmin:
                scaled = np.clip(img, cmin, cmax).astype(np.float32)
                scaled = ((scaled - cmin) / (cmax - cmin) * 255).astype(np.uint8)
                display = np.where(valid, scaled, 0)
        return display, valid

    def _get_stable_depth(self):
        """跨帧取每像素有效深度的中位数（0=无效），稳定葡萄这类闪烁深度"""
        if len(self.depth_history) < 2:
            return self.depth_img
        stack = np.stack(list(self.depth_history)).astype(np.float32)
        stack[stack <= 0] = np.nan
        med = np.nanmedian(stack, axis=0)
        return np.nan_to_num(med, nan=0).astype(np.uint16)

    def _make_depth_view(self):
        """生成深度图的彩色可视化（temporal_smooth 时显示多帧中值）"""
        src = self._get_stable_depth() if self.temporal_smooth else self.depth_img
        display, valid = self._normalize_mono16(src, clip_max=5000)
        colored = cv2.applyColorMap(display, cv2.COLORMAP_JET)
        colored[~valid] = (0, 0, 0)
        return colored, valid

    def _make_ir_view(self):
        """生成红外图的灰度可视化"""
        display, valid = self._normalize_mono16(self.ir_img, clip_max=2000)
        # 红外是单通道，转成3通道灰度
        colored = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
        return colored, valid

    def _draw_overlay(self, canvas, img_data, title, mode='depth', mx=-1, my=-1):
        """在画布上绘制叠加信息（标题、十字线、像素值）"""
        h, w = canvas.shape[:2]

        # 标题
        cv2.putText(canvas, title, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)

        # 鼠标十字线和像素值
        if 0 <= mx < w and 0 <= my < h and img_data is not None:
            val = int(img_data[my, mx])
            if mode == 'depth':
                if val > 0 and val <= 10000:
                    info = f"({mx},{my}) = {val}cm ({val*0.01:.2f}m)"
                else:
                    info = f"({mx},{my}) = {val} (invalid)"
            elif mode == 'ir':
                info = f"({mx},{my}) = {val}"
            else:
                info = ""
            cv2.putText(canvas, info, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 255), 2)
            cv2.drawMarker(canvas, (mx, my), (0, 255, 255), cv2.MARKER_CROSS, 12, 2)

        # 统计信息（模式相关）
        if mode == 'depth' and img_data is not None:
            valid_vals = img_data[(img_data > 0) & (img_data <= 10000)]
            if len(valid_vals) > 0:
                stats = (f"valid:{len(valid_vals)}px  "
                         f"min:{np.min(valid_vals)}cm  "
                         f"max:{np.max(valid_vals)}cm  "
                         f"avg:{np.mean(valid_vals):.0f}cm")
                cv2.putText(canvas, stats, (10, h - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    def run(self):
        window_name = 'Camera Viewer (depth | ir | rgb)'
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        snapshot_count = 0

        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)

            mx, my = self.mouse_x, self.mouse_y
            layout = self.layout_mode

            if self.depth_img is None:
                canvas = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(canvas, 'Waiting for camera topics...',
                            (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.imshow(window_name, canvas)
            else:
                # 生成各视图
                d_canvas, _ = self._make_depth_view()
                d_title = 'DEPTH [多帧中值]' if self.temporal_smooth else 'DEPTH'
                self._draw_overlay(d_canvas, self.depth_img, d_title, 'depth', mx, my)

                panels = [d_canvas]

                if layout == 1:
                    # 深度 + 红外
                    if self.ir_img is not None:
                        ir_canvas, _ = self._make_ir_view()
                        self._draw_overlay(ir_canvas, self.ir_img, 'IR', 'ir', mx, my)
                        panels.append(ir_canvas)
                    else:
                        blank = np.zeros_like(d_canvas)
                        cv2.putText(blank, 'No IR topic', (180, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                        panels.append(blank)

                elif layout == 2:
                    # 深度 + RGB
                    if self.rgb_img is not None:
                        rgb_display = self.rgb_img.copy()
                        cv2.putText(rgb_display, 'RGB', (10, 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        if 0 <= mx < rgb_display.shape[1] and 0 <= my < rgb_display.shape[0]:
                            cv2.drawMarker(rgb_display, (mx, my), (0, 255, 0),
                                           cv2.MARKER_CROSS, 12, 2)
                        panels.append(rgb_display)
                    else:
                        blank = np.zeros_like(d_canvas)
                        cv2.putText(blank, 'No RGB topic', (180, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                        panels.append(blank)

                elif layout == 3:
                    # 三图同显: 深度 + 红外 + RGB
                    if self.ir_img is not None:
                        ir_canvas, _ = self._make_ir_view()
                        self._draw_overlay(ir_canvas, self.ir_img, 'IR', 'ir', mx, my)
                    else:
                        ir_canvas = np.zeros_like(d_canvas)
                        cv2.putText(ir_canvas, 'No IR topic', (180, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                    panels.append(ir_canvas)

                    if self.rgb_img is not None:
                        rgb_display = self.rgb_img.copy()
                        cv2.putText(rgb_display, 'RGB', (10, 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        if 0 <= mx < rgb_display.shape[1] and 0 <= my < rgb_display.shape[0]:
                            cv2.drawMarker(rgb_display, (mx, my), (0, 255, 0),
                                           cv2.MARKER_CROSS, 12, 2)
                        panels.append(rgb_display)
                    else:
                        blank = np.zeros_like(d_canvas)
                        cv2.putText(blank, 'No RGB topic', (180, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                        panels.append(blank)

                # 将所有面板高度统一后水平拼接
                h_max = max(p.shape[0] for p in panels)
                resized = []
                for p in panels:
                    if p.shape[0] < h_max:
                        pad = np.zeros((h_max - p.shape[0], p.shape[1], 3), dtype=np.uint8)
                        p = np.vstack([p, pad])
                    resized.append(p)

                combined = np.hstack(resized)
                # 布局提示
                hint = f"Layout: [1]Depth+IR  [2]Depth+RGB  [3]All (current:{layout})"
                cv2.putText(combined, hint, (10, combined.shape[0] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
                cv2.imshow(window_name, combined)

            key = cv2.waitKey(30) & 0xFF
            if key in [27, ord('q'), ord('Q')]:
                break
            elif key == ord('s'):
                snapshot_count += 1
                filename = f'camera_snapshot_{snapshot_count}.png'
                cv2.imwrite(filename, combined)
                self.get_logger().info(f"Snapshot saved: {filename}")
            elif key == ord('1'):
                self.layout_mode = 1
                self.get_logger().info("Layout: Depth + IR")
            elif key == ord('2'):
                self.layout_mode = 2
                self.get_logger().info("Layout: Depth + RGB")
            elif key == ord('3'):
                self.layout_mode = 3
                self.get_logger().info("Layout: Depth + IR + RGB")
            elif key == ord('t'):
                self.temporal_smooth = not self.temporal_smooth
                self.get_logger().info(
                    "时间中值: " + ("ON(多帧稳定)" if self.temporal_smooth else "OFF(原始)"))

        cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)
    viewer = DepthViewer()
    try:
        viewer.run()
    except KeyboardInterrupt:
        pass
    finally:
        viewer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
