"""
FOX 葡萄采摘 — 全系统一键启动

启动必要节点（导航已包含模型/底盘/雷达/Nav2/RViz，见 fox_navigation.launch.py）:
  1. 导航（含 robot_state_publisher + 底盘 + 激光雷达 + Nav2 + RViz）
  2. 相机
  3. 机械臂
  4. 夹爪
  5. 采摘节点

用法:
  ros2 launch fox_grape_harvest full_system.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_fox_grape = get_package_share_directory('fox_grape_harvest')
    pkg_fox_nav = get_package_share_directory('fox_navigation_ros2')
    pkg_arm = get_package_share_directory('arm_controller')
    pkg_orbbec = get_package_share_directory('orbbec_camera')
    pkg_gripper = get_package_share_directory('gripper_control')

    default_config = os.path.join(pkg_fox_grape, 'config', 'harvest_config.yaml')

    return LaunchDescription([
        # ── 参数 ──
        DeclareLaunchArgument('open_rviz', default_value='true',
                              description='是否打开 RViz'),
        DeclareLaunchArgument('config_file', default_value=default_config),
        DeclareLaunchArgument('camera_calib',
                              default_value='file:///home/ubuntu/ros2fox/calib_result/camera_calib.yaml'),

        # ── 1. 导航（已含模型/底盘/雷达/Nav2/RViz） ──
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_fox_nav, 'launch', 'fox_navigation.launch.py')
            ),
            launch_arguments={
                'open_rviz': LaunchConfiguration('open_rviz'),
            }.items(),
        ),

        # ── 2. 相机 ──
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_orbbec, 'launch', 'astra_pro_plus.launch.py')
            ),
            launch_arguments={
                'color_info_url': LaunchConfiguration('camera_calib'),
            }.items(),
        ),

        # ── 3. 机械臂 ──
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_arm, 'launch', 'arm_controller.launch.py')
            ),
        ),

        # ── 4. 夹爪 ──
        Node(
            package='gripper_control',
            executable='gripper_node.py',
            name='gripper_node',
            output='screen',
        ),

        # ── 5. 采摘节点 ──
        Node(
            package='fox_grape_harvest',
            executable='grape_harvest_node',
            name='grape_harvest_node',
            output='screen',
            parameters=[{'config_file': LaunchConfiguration('config_file')}],
            emulate_tty=True,
        ),
    ])
