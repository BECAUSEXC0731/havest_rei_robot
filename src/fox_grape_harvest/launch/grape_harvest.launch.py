"""
FOX 葡萄采摘 — 一键启动 launch

启动顺序:
  1. 启动所有前置节点后（雷达、底盘、SLAM/导航、相机、机械臂）
  2. 运行此 launch 启动采摘节点

用法:
  ros2 launch fox_grape_harvest grape_harvest.launch.py \
    config_file:=/path/to/harvest_config.yaml
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_fox_grape = get_package_share_directory('fox_grape_harvest')

    default_config = os.path.join(pkg_fox_grape, 'config', 'harvest_config.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config,
            description='Path to grape harvest config YAML'
        ),

        # 主采摘节点
        Node(
            package='fox_grape_harvest',
            executable='grape_harvest_node',
            name='grape_harvest_node',
            output='screen',
            parameters=[{
                'config_file': LaunchConfiguration('config_file'),
            }],
            emulate_tty=True,
        ),
    ])
