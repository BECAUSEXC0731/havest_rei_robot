import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_fox_nav = get_package_share_directory('fox_navigation_ros2')
    pkg_fox_desc = get_package_share_directory('fox_description_ros2')
    pkg_fox_base = get_package_share_directory('rei_robot_base')

    robot_type = os.environ.get('REI_ROBOT', 'fox_three')
    # xacro 的 type 参数只需要 diff/mecanum/three（去掉 fox_ 前缀）
    xacro_type = robot_type.replace('fox_', '')

    # 机器人模型
    xacro_file = os.path.join(pkg_fox_desc, 'xacro', 'fox.xacro')
    robot_description = ParameterValue(
        Command(['xacro', ' ', xacro_file, ' type:=', xacro_type, ' sim:=0']),
        value_type=str
    )

    # Nav2 综合参数文件（包含 costmap / planner / controller / amcl / bt）
    nav2_params_file = os.path.join(pkg_fox_nav, 'param', 'nav2_params.yaml')
    # 雷达参数（frame_id=front_lidar_link，与 URDF 一致）
    lidar_params_file = os.path.join(pkg_fox_nav, 'param', 'fox_lidar_params.yaml')
    rviz_config = os.path.join(pkg_fox_nav, 'rviz', 'nav.rviz')

    return LaunchDescription([
        DeclareLaunchArgument('open_rviz', default_value='true'),

        # 1. 机器人模型
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),

        # 2. 底盘驱动
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_fox_base, 'launch', 'base.launch.py')
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

        # 4. 地图服务器
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[nav2_params_file]
        ),

        # 4.5 keepout 禁行区（掩码由 scripts/generate_keepout.py 生成）
        #     掩码黑色区=禁行 → global_costmap 的 keepout_filter 标为致命障碍，全局路径绕开
        #     remap /map→/keepout_mask 避免与真实地图 /map 冲突
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='keepout_filter_mask_server',
            output='screen',
            parameters=[{'yaml_filename': '/home/ubuntu/ros2fox/maps/keepout.yaml'}],
            remappings=[('/map', '/keepout_mask')]
        ),
        Node(
            package='nav2_map_server',
            executable='costmap_filter_info_server',
            name='keepout_costmap_filter_info_server',
            output='screen',
            parameters=[{
                # 与 nav2_params.yaml 里 global_costmap.keepout_filter.filter_info_topic 对应
                'filter_info_topic': '/keepout_filter_info',
                # 告诉 keepout_filter 去订阅哪个掩码话题
                'mask_topic': '/keepout_mask',
                # 0 = FILTER_KEEP_OUT
                'type': 0,
            }]
        ),

        # 5. 定位(lidar_loc, 替代 AMCL)
        #    jie_ware 激光“势场爬山匹配”算法移植版(ROS2): 订阅 /map + /scan +
        #    /initialpose(RViz 2D Pose Estimate), 发布 map→odom TF。普通节点,
        #    不进 lifecycle_manager(自行在收到 /map 后开始工作)。
        #    ⚠️ 与 AMCL 相同: 上电后需用 RViz 2D Pose Estimate 给一次初始位姿。
        Node(
            package='fox_navigation_ros2',
            executable='lidar_loc',
            name='lidar_loc',
            output='screen',
            parameters=[{
                'base_frame': 'base_footprint',
                'odom_frame': 'odom',
                'laser_frame': 'front_lidar_link',
                'laser_topic': '/scan',
            }]
        ),

        # 6. Nav2 导航（planner_server + controller_server + bt_navigator + recoveries）
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params_file]
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params_file]
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params_file]
        ),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params_file]
        ),

        # 7. 生命周期节点管理（自动启动 Nav2 各节点）
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'autostart': True,
                'node_names': [
                    'map_server',
                    'keepout_filter_mask_server',
                    'keepout_costmap_filter_info_server',
                    # amcl 已由 lidar_loc(普通节点)替代, 不在 lifecycle 里
                    'planner_server',
                    'controller_server',
                    'bt_navigator',
                    'behavior_server'
                ]
            }]
        ),

        # 8. RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('open_rviz'))
        ),
    ])
