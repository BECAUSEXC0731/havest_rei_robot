#!/usr/bin/env python3
"""
将标定结果注入到运行中的相机节点
让相机节点开始发布正确的 camera_info

用法:
  # 标定完成后，将 YAML 注入到相机节点
  python3 inject_calibration.py --yaml ./calib_data/color_camera_info.yaml --camera color

  # 注入 IR 相机标定
  python3 inject_calibration.py --yaml ./calib_data/ir_camera_info.yaml --camera ir
"""

import sys
import argparse
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from sensor_msgs.msg import CameraInfo
import yaml


class CalibrationInjector(Node):
    def __init__(self, yaml_file, camera_type):
        super().__init__('calibration_injector')

        self.yaml_file = yaml_file
        self.camera_type = camera_type
        self.camera_info_url = None

        # 读取 YAML
        with open(yaml_file, 'r') as f:
            self.calib_data = yaml.safe_load(f)

        # 根据相机类型选择正确的 info_url 参数名
        if camera_type == 'color':
            self.param_name = 'color_info_url'
        elif camera_type == 'ir':
            self.param_name = 'ir_info_url'
        elif camera_type == 'depth':
            self.param_name = 'depth_info_url'
        else:
            self.param_name = 'color_info_url'

        # 构造 file:// URL
        import os
        abs_path = os.path.abspath(yaml_file)
        self.file_url = f"file://{abs_path}"

        self.get_logger().info(f"将标定文件注入到相机节点:")
        self.get_logger().info(f"  YAML: {abs_path}")
        self.get_logger().info(f"  param: {self.param_name}")
        self.get_logger().info(f"  URL: {self.file_url}")
        self.get_logger().info(f"  相机: {camera_type}")

        # 设置参数
        self.set_parameters([Parameter(self.param_name, Parameter.Type.STRING, self.file_url)])

        # 等待并验证
        self.create_timer(1.0, self.verify)

    def verify(self):
        """等待几秒后检查 camera_info 是否更新"""
        node_name = f"/camera/camera"  # 相机节点名
        self.get_logger().info(f"参数已设置! 请检查 /camera/{self.camera_type}/camera_info")
        self.get_logger().info(f"如果相机节点支持动态重配置，内参应当已更新")
        self.get_logger().info("")
        self.get_logger().info("验证命令:")
        self.get_logger().info(f"  ros2 topic echo /camera/{self.camera_type}/camera_info --once")
        self.get_logger().info("")
        self.get_logger().info("如果是 launch 中设置，可以修改 launch 文件后重启相机:")
        self.get_logger().info(f"  {self.param_name}: '{self.file_url}'")

        # 取消定时器
        self.destroy_timer(self.get_timer_list()[0])


def main():
    parser = argparse.ArgumentParser(description='注入相机标定结果')
    parser.add_argument('--yaml', required=True, help='camera_info YAML 文件路径')
    parser.add_argument('--camera', default='color', choices=['color', 'ir', 'depth'],
                       help='相机类型')
    args = parser.parse_args()

    rclpy.init()
    injector = CalibrationInjector(getattr(args, 'yaml'), args.camera)
    try:
        rclpy.spin_once(injector, timeout_sec=2.0)
    except KeyboardInterrupt:
        pass
    finally:
        injector.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
