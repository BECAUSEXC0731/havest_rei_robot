"""
FOX 葡萄采摘 — 全系统一键启动

启动必要节点（导航已包含模型/底盘/雷达/Nav2/RViz，见 fox_navigation.launch.py）:
  1. 导航（含 robot_state_publisher + 底盘 + 激光雷达 + Nav2 + RViz）
  2. 相机（默认加载【标定好的】彩色 + IR 内参）
  3. 机械臂
  4. 夹爪
  5. 采摘节点

用法:
  ros2 launch fox_grape_harvest full_system.launch.py

相机内参（默认值 = 本项目标定结果，决定手眼标定/像素→3D 的尺度）:
  color_info_url:=file:///home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml
  ir_info_url:=file:///home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml

如需临时换回其它内参文件，用同名 launch 参数覆盖即可，例如:
  ros2 launch fox_grape_harvest full_system.launch.py \
    color_info_url:=file:///home/ubuntu/ros2fox/calib_result/camera_calib.yaml
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

    # 相机内参默认值：本项目标定结果（彩色 fx≈607、IR 内参）
    # 为什么要显式指定：camera_info 话题的内参由它决定 → 直接决定手眼标定与
    # 像素→3D 的尺度正确性；用驱动的出厂内参会导致抓取位置系统性偏移。
    default_color_info = ('file:///home/ubuntu/ros2fox/calib_data/color/'
                          'color_camera_info.yaml')
    default_ir_info = ('file:///home/ubuntu/ros2fox/calib_data/ir/'
                       'ir_camera_info.yaml')

    return LaunchDescription([
        # ── 参数 ──
        DeclareLaunchArgument('open_rviz', default_value='true',
                              description='是否打开 RViz'),
        DeclareLaunchArgument('config_file', default_value=default_config),
        DeclareLaunchArgument('color_info_url', default_value=default_color_info,
                              description='彩色相机内参 YAML (file:// URL)，默认=标定结果'),
        DeclareLaunchArgument('ir_info_url', default_value=default_ir_info,
                              description='IR/深度相机内参 YAML (file:// URL)，默认=标定结果'),

        # ── 1. 导航（已含模型/底盘/雷达/Nav2/RViz） ──
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_fox_nav, 'launch', 'fox_navigation.launch.py')
            ),
            launch_arguments={
                'open_rviz': LaunchConfiguration('open_rviz'),
            }.items(),
        ),

        # ── 2. 相机（彩色 + IR 内参都用标定结果） ──
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_orbbec, 'launch', 'astra_pro_plus.launch.py')
            ),
            launch_arguments={
                'color_info_url': LaunchConfiguration('color_info_url'),
                'ir_info_url': LaunchConfiguration('ir_info_url'),
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
