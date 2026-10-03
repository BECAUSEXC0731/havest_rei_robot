#!/usr/bin/env python3
"""
葡萄夹取测试脚本

检测葡萄 → 3D 定位(机器人坐标, 手眼+D2C) → 选择最合适的可抓取葡萄 →
机械臂移动到目标 + 夹爪(gripper_control)夹紧 → 抬升

依赖(需先启动):
  相机(带新内参)   ros2 launch orbbec_camera astra_pro_plus.launch.py \
                      color_info_url:=file:///home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml \
                      ir_info_url:=file:///home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml
  机械臂           ros2 launch arm_controller arm_controller.launch.py
  夹爪             ros2 launch gripper_control gripper.launch.py

用法:
  ros2 run fox_grape_harvest grape_grasp_test.py

按键:
  空格       夹取当前最合适的可抓取葡萄
  q / ESC    退出
"""
import os
import sys
import time
import math
from collections import deque

import cv2
import numpy as np
import yaml
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from arm_controller.srv import Move
from std_srvs.srv import SetBool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fox_grape_harvest.yolo_detector import YoloDetector
from fox_grape_harvest.depth_utils import (
    load_hand_eye_calibration, load_d2c_config,
    depth_to_robot_3d_nearest_in_box,
    load_grasp_check, classify_reach,
)

CONFIG = '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml'


class GrapeGraspTest(Node):
    """葡萄夹取测试节点。"""

    def __init__(self):
        super().__init__('grape_grasp_test')
        self.bridge = CvBridge()

        # ── 配置 ──
        with open(CONFIG) as f:
            cfg = yaml.safe_load(f)
        arm_cfg = cfg.get('arm', {}) or {}
        self.ws = {
            'x_min': arm_cfg.get('workspace_x_min', 30),
            'x_max': arm_cfg.get('workspace_x_max', 320),
            'y_min': arm_cfg.get('workspace_y_min', -180),
            'y_max': arm_cfg.get('workspace_y_max', 180),
            'z_min': arm_cfg.get('workspace_z_min', 20),
            'z_max': arm_cfg.get('workspace_z_max', 220),
        }
        # 可抓性判定参数（容度）：margin / 临界容差带 / 半径约束 / 自适应裕度
        self.gc = load_grasp_check(cfg)
        self.pref = (arm_cfg.get('preferred_x', 200),
                     arm_cfg.get('preferred_y', 0),
                     arm_cfg.get('preferred_z', 130))
        # 夹爪 TCP 偏移(mm): 夹爪接触点相对机械臂参考点的偏移。
        # 参考点目标 = 葡萄坐标 + tool_offset（夹爪比参考点低 → tool_offset_z 为正）
        self.tool_off = (arm_cfg.get('tool_offset_x', 0.0),
                         arm_cfg.get('tool_offset_y', 0.0),
                         arm_cfg.get('tool_offset_z', 0.0))
        self.grip_delay = arm_cfg.get('grip_delay', 1.0)
        # 夹取完成后回到的安全点（机械臂参考点，mm）
        self.home = (arm_cfg.get('home_x', 0),
                     arm_cfg.get('home_y', -180),
                     arm_cfg.get('home_z', 30))
        # 抓取过渡点（机械臂参考点，mm）：抓取前先到这里再去抓取点。
        # config 未配置 transition_* 时，自动取工作空间范围中点。
        _mid = (
            (self.ws['x_min'] + self.ws['x_max']) / 2.0,
            (self.ws['y_min'] + self.ws['y_max']) / 2.0,
            (self.ws['z_min'] + self.ws['z_max']) / 2.0,
        )
        self.transition = (
            float(arm_cfg.get('transition_x', _mid[0])),
            float(arm_cfg.get('transition_y', _mid[1])),
            float(arm_cfg.get('transition_z', _mid[2])),
        )

        model_path = cfg.get('yolo_model_path',
                             '/home/ubuntu/ros2fox/models/grape.pt')
        calib_path = cfg.get('hand_eye_calib_path',
                             '/home/ubuntu/ros2fox/calib_result/hand_eye_result.json')
        d2c_path = cfg.get('d2c_extrinsic_path',
                           '/home/ubuntu/ros2fox/calib_result/color_ir_extrinsic.json')
        ir_info_path = cfg.get('ir_camera_info_path',
                               '/home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml')

        # ── 标定/模型 ──
        self.T_cam_to_robot = load_hand_eye_calibration(calib_path)
        self.d2c = load_d2c_config(d2c_path, ir_info_path)
        if self.d2c is not None:
            self.K_ir, self.T_color_to_ir = self.d2c
            self.get_logger().info("✅ D2C(手动深度对齐) 已加载")
        else:
            self.K_ir = None
            self.T_color_to_ir = None
            self.get_logger().warn("⚠ 无 D2C 配置，深度按未对齐处理")

        if os.path.exists(model_path):
            self.detector = YoloDetector(model_path, cfg.get('yolo_confidence', 0.5))
            self.get_logger().info(f"✅ YOLO: {model_path}")
        else:
            self.detector = None
            self.get_logger().error(f"❌ 模型不存在: {model_path}")

        # ── 相机数据 ──
        self.latest_rgb = None
        self.latest_depth = None
        self.depth_history = deque(maxlen=7)
        self.camera_matrix = None

        # ── 服务客户端 ──
        self.goto_cli = self.create_client(Move, 'goto_position')
        self.grip_cli = self.create_client(SetBool, 'gripper/grip')
        for name, cli in (('goto_position', self.goto_cli),
                          ('gripper/grip', self.grip_cli)):
            if not cli.wait_for_service(timeout_sec=5.0):
                self.get_logger().warn(f"⚠ 服务 {name} 不可用")

        # ── 订阅 ──
        self.create_subscription(Image, '/camera/color/image_raw',
                                 self._rgb_cb, qos_profile_sensor_data)
        self.create_subscription(Image, '/camera/depth/image_raw',
                                 self._depth_cb, qos_profile_sensor_data)
        self.create_subscription(CameraInfo, '/camera/color/camera_info',
                                 self._info_cb, 1)

        self.get_logger().info("=" * 55)
        self.get_logger().info("葡萄夹取测试就绪: 空格=夹取  q/ESC=退出")
        self.get_logger().info(
            f"工具偏移(mm): x={self.tool_off[0]:.0f} y={self.tool_off[1]:.0f} z={self.tool_off[2]:.0f}")
        self.get_logger().info(
            f"过渡点(mm,工作范围中点): x={self.transition[0]:.0f} "
            f"y={self.transition[1]:.0f} z={self.transition[2]:.0f}")
        self.get_logger().info(
            f"判定容度: margin_xy={self.gc['margin_xy_mm']:.0f} "
            f"margin_z={self.gc['margin_z_mm']:.0f} "
            f"容差带={self.gc['marginal_mm']:.0f}mm")
        self.get_logger().info("=" * 55)

    # ── 回调 ──
    def _info_cb(self, msg):
        if self.camera_matrix is not None:
            return
        k = np.array(msg.k).reshape(3, 3)
        if k[0, 0] == 0 or np.any(np.isnan(k)):
            return
        self.camera_matrix = k
        self.get_logger().info(f"相机内参: fx={k[0, 0]:.1f}")

    def _rgb_cb(self, msg):
        try:
            self.latest_rgb = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception:
            pass

    def _depth_cb(self, msg):
        try:
            depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            if depth.dtype == np.uint16:
                # 本相机深度单位是厘米! /100 转米
                depth = depth.astype(np.float32) / 100.0
            self.latest_depth = depth
            self.depth_history.append(depth)
        except Exception as e:
            self.get_logger().warn(f"深度转换失败: {e}")

    # ── 可抓取性 ──
    def _graspability(self, x, y, z):
        """可抓性分级：返回 (level, code)。

        level 0=GRASP(完全可达) / 1=MARGINAL(临界可达，在容差带内) / 2=NO。
        判定只用"工作空间盒 + 可选半径/自适应裕度"，不参与 3D 计算，
        因此放宽判定容度不会损失定位精度。
        """
        return classify_reach(x, y, z, self.ws, self.gc)

    # ── 机械臂/夹爪 ──
    def _call_goto(self, x, y, z):
        req = Move.Request()
        req.pose.position.x = float(x)
        req.pose.position.y = float(y)
        req.pose.position.z = float(z)
        future = self.goto_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=30)
        if not future.done() or future.result() is None:
            return False
        return bool(future.result().success)

    def _call_grip(self, close):
        req = SetBool.Request()
        req.data = close
        future = self.grip_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10)
        if not future.done() or future.result() is None:
            return False
        return bool(future.result().success)

    def _tool_offset_robot(self, x, y, z):
        """把夹爪【局部坐标系】偏移旋转到机器人坐标系。

        局部系定义（机械臂基座为原点）：
          tool_offset_x: 沿机械臂指向目标的径向方向
          tool_offset_y: 侧向（垂直径向，向左为正）
          tool_offset_z: 垂直方向（不受朝向影响）
        机械臂朝向 θ = atan2(y, x)。
        这样葡萄在左/右/前不同位姿时，偏移都能正确补偿，
        避免常数偏移在机器人 Y 上随朝向变化导致“往前调好往后又偏”。
        """
        ox_l, oy_l, oz_l = self.tool_off
        theta = math.atan2(y, x)
        c, s = math.cos(theta), math.sin(theta)
        ox_r = ox_l * c - oy_l * s
        oy_r = ox_l * s + oy_l * c
        return ox_r, oy_r, oz_l

    def grasp(self, target):
        """夹取一颗葡萄: target = (x, y, z) 葡萄机器人坐标(mm)；完成后直接回安全点放下

        流程: 先到过渡点(工作空间中点) → 到补偿后的抓取位置 → 夹紧 → 回安全点 → 松开
        (无预定位抬升、也无抓取后抬升)
        """
        x, y, z = target
        # 参考点目标 = 葡萄坐标 + 工具偏移(局部→按朝向旋转到机器人系)
        ox, oy, oz = self._tool_offset_robot(x, y, z)
        gx = x + ox
        gy = y + oy
        gz = z + oz
        hx, hy, hz = self.home
        tx, ty, tz = self.transition
        self.get_logger().info(
            f"🍇 夹取葡萄 ({x:.0f},{y:.0f},{z:.0f}) → 参考点({gx:.0f},{gy:.0f},{gz:.0f})")
        ok = True
        # 1. 先到过渡点（工作空间范围中点），避免从当前位置直接斜插到抓取点
        self.get_logger().info(f"↗ 先到过渡点 ({tx:.0f},{ty:.0f},{tz:.0f})")
        if not self._call_goto(tx, ty, tz):
            self.get_logger().error("移动到过渡点失败"); ok = False
        time.sleep(0.5)
        # 2. 移动到补偿后的抓取位置
        if ok and not self._call_goto(gx, gy, gz):
            self.get_logger().error("移动到抓取位置失败"); ok = False
        time.sleep(0.5)
        # 3. 夹紧
        if ok and not self._call_grip(True):
            self.get_logger().error("夹爪失败"); ok = False
        time.sleep(self.grip_delay)
        # 4. 直接回到安全点（不再先抬升），到位后放下葡萄
        self.get_logger().info(f"🛡 回到安全点 ({hx:.0f},{hy:.0f},{hz:.0f})")
        self._call_goto(hx, hy, hz)
        # 5. 松开夹爪（把葡萄放下）
        self.get_logger().info("🖐 在安全点松开夹爪")
        self._call_grip(False)
        self.get_logger().info(
            "✅ 夹取流程结束(已回安全点并松开)" if ok else "⚠ 夹取失败(已回安全点)")
        return ok

    # ── 主循环一次 ──
    def run_once(self):
        """检测+定位+显示；返回最合适的可抓取葡萄坐标(mm)或 None。"""
        if (self.latest_rgb is None or self.latest_depth is None
                or self.camera_matrix is None or self.detector is None):
            return None

        rgb = self.latest_rgb.copy()
        depth = self.latest_depth.copy()
        detections = self.detector.detect(rgb)
        img = self.detector.draw_detections(rgb, detections)

        frames = list(self.depth_history) if self.depth_history else [depth]
        best = None
        best_dist = float('inf')
        graspable_cnt = 0
        for det in detections:
            cx, cy = det['center']
            if self.T_color_to_ir is not None:
                pt_mm, d_m = depth_to_robot_3d_nearest_in_box(
                    det['bbox'], frames, self.camera_matrix, self.K_ir,
                    self.T_color_to_ir, self.T_cam_to_robot)
            else:
                pt_mm, d_m = None, None
            if pt_mm is not None:
                x, y, z = pt_mm
                level, code = self._graspability(x, y, z)
                # MARGINAL(临界可达)也算可抓 → 提升容度(仅扩展容差带，不改 3D 精度)
                if level <= 1:
                    graspable_cnt += 1
                    dist = ((x - self.pref[0]) ** 2 + (y - self.pref[1]) ** 2
                            + (z - self.pref[2]) ** 2) ** 0.5
                    if dist < best_dist:
                        best_dist = dist
                        best = (x, y, z)
                # 绿=完全可达  琥珀=临界可达  红=不可达
                color = (0, 255, 0) if level == 0 else (
                    (0, 165, 255) if level == 1 else (0, 0, 255))
                label = f"({x:.0f},{y:.0f},{z:.0f}) {code} d={d_m*100:.0f}cm"
                cv2.putText(img, label, (cx - 90, cy + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            else:
                cv2.putText(img, "no depth", (cx - 60, cy + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)

        cv2.putText(img,
                    f"Detected:{len(detections)} Graspable:{graspable_cnt}  "
                    f"SPACE=抓取  q=退出",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        try:
            cv2.imshow('Grape Grasp Test', img)
            cv2.waitKey(1)
        except Exception:
            pass
        return best


def main():
    rclpy.init()
    node = GrapeGraspTest()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            target = node.run_once()
            key = -1
            try:
                key = cv2.waitKey(1) & 0xFF
            except Exception:
                pass
            if key in (ord('q'), 27):
                break
            if key == ord(' ') and target is not None:
                node.grasp(target)
    except KeyboardInterrupt:
        pass
    finally:
        # ⚠️ 退出清理逐步兜异常（2026-09-21）：无 DISPLAY 时 cv2.destroyAllWindows() 会抛
        #    cv2.error；Ctrl-C 后 ROS context 可能已被 rclpy 的 SIGINT 处理关掉，
        #    destroy_node()/shutdown() 也会抛 → 不兜就会刷一段 traceback（看着像崩了）
        for step, fn in (
            ("关闭窗口", cv2.destroyAllWindows),
            ("销毁节点", node.destroy_node),
            ("rclpy 关闭", lambda: rclpy.shutdown() if rclpy.ok() else None),
        ):
            try:
                fn()
            except Exception as exc:
                print(f"[退出] {step}异常（忽略）: {exc}")


if __name__ == '__main__':
    main()
