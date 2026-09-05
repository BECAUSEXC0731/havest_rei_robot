#!/usr/bin/env python3
"""
Orbbec Astra Pro Plus 相机标定工具

支持标定:
  - 彩色相机 (color)
  - 红外相机 (ir)
  - 深度相机 (depth)

用法:
  步骤1 - 采集标定图像:
    python3 calibrate_camera.py capture --topic color  --dir ./calib_data/color
    python3 calibrate_camera.py capture --topic ir     --dir ./calib_data/ir

  步骤2 - 计算内参:
    python3 calibrate_camera.py calibrate --dir ./calib_data/color --size 8x6 --square 30
    python3 calibrate_camera.py calibrate --dir ./calib_data/ir    --size 8x6 --square 30

  步骤3 - 生成 ROS2 camera_info YAML:
    python3 calibrate_camera.py save --dir ./calib_data/color --camera color --output ./calib_data/color_camera_info.yaml
"""

import sys
import os
import argparse
import cv2
import numpy as np
import json
import yaml
from glob import glob
from pathlib import Path


# ============================================================
# 步骤1: 采集标定图像
# ============================================================
def capture(args):
    """从相机话题采集棋盘格图像"""
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from cv_bridge import CvBridge

    topic_map = {
        'color': '/camera/color/image_raw',
        'ir': '/camera/ir/image_raw',
        'depth': '/camera/depth/image_raw',
    }

    topic = topic_map.get(args.topic, args.topic)
    save_dir = Path(args.dir).resolve()  # 转为绝对路径
    save_dir.mkdir(parents=True, exist_ok=True)

    # 棋盘格参数
    pattern_size = tuple(int(x) for x in args.size.split('x'))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    class CaptureNode(Node):
        def __init__(self):
            super().__init__('calibration_capture')
            self.bridge = CvBridge()
            self.latest_img = None
            self.count = 0
            self.sub = self.create_subscription(
                Image, topic, self.callback, 1)

        def callback(self, msg):
            try:
                # 对 IR/Depth 这类 MONO16 做归一化再检测棋盘格
                raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                if raw.dtype == np.uint16 and len(raw.shape) == 2:
                    # 16位单通道 → 归一化到 8 位
                    norm = cv2.normalize(raw, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                    display = cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)
                    gray = norm
                elif len(raw.shape) == 3:
                    gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
                    display = raw.copy()
                else:
                    gray = raw
                    display = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)
                self.latest_img = (raw, gray, display)
            except Exception as e:
                self.get_logger().warn(f"Image conversion error: {e}")

    rclpy.init()
    node = CaptureNode()
    abs_save = str(save_dir)
    node.get_logger().info("=" * 50)
    node.get_logger().info(f"采集标定图像")
    node.get_logger().info(f"  话题: {topic}")
    node.get_logger().info(f"  棋盘格: {args.size} 内角点")
    node.get_logger().info(f"  保存到: {abs_save}")
    node.get_logger().info(f"按键: SPACE=保存  ESC=退出  r=重置计数")
    node.get_logger().info("=" * 50)

    cv2.namedWindow("Calibration Capture")
    last_save_msg = ""  # 用于在画面上显示最近保存信息

    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.05)

        if node.latest_img is None:
            canvas = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(canvas, f"Waiting for {topic} ...",
                        (100, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(canvas, "Is the camera launched?",
                        (140, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 1)
            cv2.imshow("Calibration Capture", canvas)
            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                break
            continue

        raw_img, gray, display = node.latest_img

        # 增强对比度，提高棋盘格检测成功率
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # 使用 ADAPTIVE_THRESH 标志提高检测鲁棒性
        chessboard_flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        found, corners = cv2.findChessboardCorners(enhanced, pattern_size, chessboard_flags)

        if found:
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            cv2.drawChessboardCorners(display, pattern_size, corners_refined, found)

        # OSD 信息
        status = "CHESSBOARD OK" if found else "No chessboard"
        status_color = (0, 255, 0) if found else (0, 0, 255)

        # 顶部状态栏
        cv2.putText(display, f"Saved: {node.count}  [{status}]",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(display, f"Save dir: {abs_save}",
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
        cv2.putText(display, "SPACE=save  ESC=quit  r=reset",
                    (10, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # 底部提示
        if last_save_msg:
            cv2.putText(display, last_save_msg, (10, display.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # 保存数进度提示
        if node.count > 0:
            progress = min(node.count / 15, 1.0)
            bar_w = int(200 * progress)
            cv2.rectangle(display, (display.shape[1] - 220, 10),
                          (display.shape[1] - 20, 25), (60, 60, 60), -1)
            cv2.rectangle(display, (display.shape[1] - 220, 10),
                          (display.shape[1] - 220 + bar_w, 25), (0, 200, 0), -1)
            cv2.putText(display, f"{node.count}/15+",
                        (display.shape[1] - 80, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        cv2.imshow("Calibration Capture", display)
        key = cv2.waitKey(30) & 0xFF

        if key == 27:  # ESC
            break
        elif key == ord('r'):
            node.count = 0
            last_save_msg = ""
            node.get_logger().info("计数已重置")
        elif key == ord(' '):
            if found:
                fname = save_dir / f"image_{node.count:04d}.png"
                cv2.imwrite(str(fname), raw_img)
                node.count += 1
                last_save_msg = f"Saved: image_{node.count-1:04d}.png  ({node.count} total)"
                node.get_logger().info(f"[OK] 已保存: {fname}")
                if node.count >= 15:
                    node.get_logger().info("已达到建议数量(15+)！按 ESC 退出并开始标定。")
            else:
                last_save_msg = "Cannot save: chessboard not detected!"
                node.get_logger().warn("棋盘格未检测到，无法保存！请调整角度/距离/光照。")

    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()
    saved_path = str(save_dir)
    print(f"\n{'='*50}")
    print(f"  采集完成！共保存 {node.count} 张图像")
    print(f"  保存路径: {saved_path}")
    print(f"{'='*50}")
    if node.count < 5:
        print(f"  [WARN] 图像太少 ({node.count})，建议至少 15 张")
    elif node.count < 15:
        print(f"  [OK] 可以尝试标定，但建议采集更多图像 (15+)")
    else:
        print(f"  [GOOD] 图像数量充足，可以开始标定！")


# ============================================================
# 步骤2: 计算内参
# ============================================================
def calibrate(args):
    """从采集的图像计算相机内参"""
    data_dir = Path(args.dir)
    image_files = sorted(glob(str(data_dir / "*.png")))

    if len(image_files) < 5:
        print(f"[ERROR] 图像太少 ({len(image_files)})，至少需要 5 张，建议 15-20 张")
        sys.exit(1)

    pattern_size = tuple(int(x) for x in args.size.split('x'))
    square_size = args.square / 1000.0  # mm -> m

    print(f"[INFO] 加载 {len(image_files)} 张图像...")
    print(f"[INFO] 棋盘格: {pattern_size[0]}x{pattern_size[1]} 内角点, 每格 {args.square}mm")

    # 准备棋盘格3D坐标
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = []  # 3D 点
    imgpoints = []  # 2D 点
    image_shape = None

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for fpath in image_files:
        img = cv2.imread(fpath)
        if img is None:
            print(f"  [WARN] 无法读取: {fpath}")
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        image_shape = gray.shape[::-1]  # (width, height)

        found, corners = cv2.findChessboardCorners(gray, pattern_size, None)
        if found:
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints.append(corners_refined)
            print(f"  [OK] {Path(fpath).name}: 检测到棋盘格")
        else:
            print(f"  [SKIP] {Path(fpath).name}: 未检测到棋盘格")

    if len(objpoints) < 5:
        print(f"[ERROR] 有效图像太少 ({len(objpoints)})，请重新采集")
        sys.exit(1)

    print(f"\n[INFO] 使用 {len(objpoints)} 张图像进行标定...")

    # 标定
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, image_shape, None, None
    )

    print(f"\n{'='*50}")
    print(f"标定结果 (重投影误差: {ret:.6f})")
    print(f"{'='*50}")
    print(f"\n相机矩阵 K:")
    print(f"  fx = {mtx[0, 0]:.6f}")
    print(f"  fy = {mtx[1, 1]:.6f}")
    print(f"  cx = {mtx[0, 2]:.6f}")
    print(f"  cy = {mtx[1, 2]:.6f}")
    print(f"\n畸变系数 (k1, k2, p1, p2, k3):")
    print(f"  {dist.ravel()[:5]}")
    print(f"\n图像尺寸: {image_shape[0]}x{image_shape[1]}")

    # 保存结果
    result_file = data_dir / "calibration_result.npz"
    np.savez(str(result_file),
             mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs,
             image_width=image_shape[0], image_height=image_shape[1],
             ret=ret, pattern_size=pattern_size, square_size=square_size)
    print(f"\n[OK] 结果已保存: {result_file}")

    # 生成 ROS camera_info YAML
    camera_name = args.camera if args.camera else data_dir.name
    yaml_file = data_dir / f"{camera_name}_camera_info.yaml"
    _save_ros_yaml(yaml_file, mtx, dist, image_shape, camera_name)
    print(f"[OK] ROS camera_info 已保存: {yaml_file}")

    # 显示标定质量
    _show_calibration_quality(objpoints, imgpoints, rvecs, tvecs, mtx, dist, image_shape, data_dir)

    return mtx, dist, image_shape


def _convert_numpy(obj):
    """递归将 numpy 类型转为 Python 原生类型"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [_convert_numpy(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    return obj


def _save_ros_yaml(filepath, mtx, dist, image_shape, camera_name):
    """保存为 ROS2 camera_info YAML 格式 (纯原生类型, 无 numpy 对象)"""
    data = {
        'camera_name': camera_name,
        'image_width': int(image_shape[0]),
        'image_height': int(image_shape[1]),
        'camera_matrix': {
            'rows': 3, 'cols': 3,
            'data': _convert_numpy(mtx.ravel().tolist())
        },
        'distortion_model': 'rational_polynomial',
        'distortion_coefficients': {
            'rows': 1, 'cols': 8,
            'data': _convert_numpy([
                float(dist[0, 0]), float(dist[0, 1]),
                float(dist[0, 2]), float(dist[0, 3]),
                float(dist[0, 4]), 0.0, 0.0, 0.0
            ])
        },
        'rectification_matrix': {
            'rows': 3, 'cols': 3,
            'data': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        },
        'projection_matrix': {
            'rows': 3, 'cols': 4,
            'data': _convert_numpy([
                float(mtx[0, 0]), 0.0, float(mtx[0, 2]), 0.0,
                0.0, float(mtx[1, 1]), float(mtx[1, 2]), 0.0,
                0.0, 0.0, 1.0, 0.0
            ])
        }
    }
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    # 验证写入的文件不含 numpy 对象
    content = open(filepath).read()
    if 'numpy' in content or '!!python' in content:
        print("[WARN] YAML 文件仍包含 Python 对象，尝试替代方案...")
        # 用更安全的方式重新写入
        import json
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[WARN] 已改用 JSON 格式保存: {filepath}")


def _show_calibration_quality(objpoints, imgpoints, rvecs, tvecs, mtx, dist,
                               image_shape, data_dir):
    """评估标定质量: 显示重投影误差分布"""
    errors = []
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        errors.append(error)

    errors = np.array(errors)
    print(f"\n重投影误差统计:")
    print(f"  平均: {np.mean(errors):.4f} px")
    print(f"  最大: {np.max(errors):.4f} px")
    print(f"  最小: {np.min(errors):.4f} px")
    print(f"  标准差: {np.std(errors):.4f} px")
    if np.mean(errors) < 0.3:
        print(f"  [EXCELLENT] 标定质量非常好!")
    elif np.mean(errors) < 0.5:
        print(f"  [GOOD] 标定质量很好!")
    elif np.mean(errors) < 1.0:
        print(f"  [OK] 标定质量可接受")
    else:
        print(f"  [WARN] 标定质量一般 (建议重新采集)")

    # 可视化误差
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.bar(range(len(errors)), errors)
        plt.xlabel('Image index')
        plt.ylabel('Reprojection error (px)')
        plt.title('Per-image Reprojection Error')
        plt.axhline(y=np.mean(errors), color='r', linestyle='--', label=f'Mean: {np.mean(errors):.4f}')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.hist(errors, bins=20)
        plt.xlabel('Reprojection error (px)')
        plt.ylabel('Count')
        plt.title('Error Distribution')

        plt.tight_layout()
        plot_file = data_dir / 'calibration_quality.png'
        plt.savefig(str(plot_file))
        print(f"[OK] 质量图已保存: {plot_file}")
    except ImportError:
        print("[WARN] matplotlib 未安装，跳过绘图")


# ============================================================
# 步骤3: 保存 ROS2 camera_info YAML
# ============================================================
def save_yaml(args):
    """从已有的 npz 结果文件生成 ROS2 camera_info YAML"""
    data_dir = Path(args.dir)

    # 尝试加载 npz 结果
    npz_file = data_dir / "calibration_result.npz"
    if not npz_file.exists():
        print(f"[ERROR] 找不到标定结果: {npz_file}")
        print(f"       请先运行 'calibrate' 命令")
        sys.exit(1)

    data = np.load(str(npz_file))
    mtx = data['mtx']
    dist = data['dist']
    image_shape = (int(data['image_width']), int(data['image_height']))

    camera_name = args.camera if args.camera else data_dir.name
    output = args.output if args.output else data_dir / f"{camera_name}_camera_info.yaml"

    _save_ros_yaml(output, mtx, dist, image_shape, camera_name)
    print(f"[OK] ROS camera_info YAML 已保存: {output}")
    print(f"\n使用方法: 将 YAML 文件路径传递给相机节点参数:")
    print(f"  ros2 param set /camera/camera color_info_url file://{output.absolute()}")
    print(f"  或添加到 launch 文件中:")
    print(f"    <param name=\"color_info_url\" value=\"file://{output.absolute()}\"/>")


# ============================================================
# 主入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='相机标定工具')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # capture
    p_cap = subparsers.add_parser('capture', help='采集标定图像')
    p_cap.add_argument('--topic', default='color', choices=['color', 'ir', 'depth'],
                       help='相机话题类型')
    p_cap.add_argument('--dir', default='./calib_data',
                       help='保存目录')
    p_cap.add_argument('--size', default='8x6',
                       help='棋盘格内角点 (宽x高)')

    # calibrate
    p_cal = subparsers.add_parser('calibrate', help='计算内参')
    p_cal.add_argument('--dir', required=True, help='图像目录')
    p_cal.add_argument('--size', default='8x6', help='棋盘格内角点 (宽x高)')
    p_cal.add_argument('--square', type=float, default=30, help='格子边长 (mm)')
    p_cal.add_argument('--camera', default=None, help='相机名称')

    # save yaml
    p_save = subparsers.add_parser('save', help='生成 ROS camera_info YAML')
    p_save.add_argument('--dir', required=True, help='标定结果目录')
    p_save.add_argument('--camera', default=None, help='相机名称')
    p_save.add_argument('--output', default=None, help='输出 YAML 文件路径')

    args = parser.parse_args()

    if args.command == 'capture':
        capture(args)
    elif args.command == 'calibrate':
        calibrate(args)
    elif args.command == 'save':
        save_yaml(args)


if __name__ == '__main__':
    main()
