import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_fox_slam = get_package_share_directory('fox_slam_ros2')
    pkg_fox_description = get_package_share_directory('fox_description_ros2')
    pkg_rei_robot_base = get_package_share_directory('rei_robot_base')

    # 根据环境变量 REI_ROBOT 选择底盘型号
    robot_type = os.environ.get('REI_ROBOT', 'fox_three')
    # xacro 的 type 参数只需要 diff/mecanum/three（去掉 fox_ 前缀）
    xacro_type = robot_type.replace('fox_', '')

    # ── 参数路径 ──
    cartographer_config_dir = os.path.join(pkg_fox_slam, 'config')
    lidar_params_file = os.path.join(pkg_fox_slam, 'config', 'fox_lidar_params.yaml')
    rviz_config = os.path.join(pkg_fox_slam, 'rviz', 'slam.rviz')

    # ── 机器人模型 ──
    xacro_file = os.path.join(pkg_fox_description, 'xacro', 'fox.xacro')
    robot_description = ParameterValue(
        Command(['xacro', ' ', xacro_file, ' type:=', xacro_type, ' sim:=0']),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument('open_rviz', default_value='true'),

        # 1. 机器人模型 + robot_state_publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),

        # 2. 底盘驱动
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_rei_robot_base, 'launch', 'base.launch.py')
            ),
        ),

        # 3. 激光雷达
        Node(
            package='ydlidar_ros2_driver',
            executable='ydlidar_ros2_driver_node',
            name='ydlidar_ros2_driver_node',
            parameters=[lidar_params_file],
            output='screen'
        ),

        # 4. Cartographer（图优化 SLAM）
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': False}],
            arguments=['-configuration_directory', cartographer_config_dir,
                       '-configuration_basename', 'cartographer_fox.lua'],
            # Cartographer 内部订阅的里程计话题名为 odometry，重映射到 /odom
            remappings=[('odometry', '/odom')]
        ),

        # 5. 占用栅格地图发布（供 RViz / map_saver 使用）
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'resolution': 0.05,
                'publish_period_sec': 1.0
            }]
        ),

        # 6. RViz 可视化
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('open_rviz'))
        ),
    ])
