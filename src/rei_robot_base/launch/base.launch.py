import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 直接从环境变量读取，因为需要用于 Python 字符串拼接
    robot_type = os.environ.get('REI_ROBOT', 'fox_three')

    config_file = os.path.join(
        get_package_share_directory('rei_robot_base'),
        'config',
        f'{robot_type}.yaml'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'base_config_file',
            default_value=config_file,
            description='Path to robot base config YAML'
        ),
        Node(
            package='rei_robot_base',
            executable='robot_base_node',
            name='rei_base',
            parameters=[LaunchConfiguration('base_config_file')],
            output='screen'
        ),
    ])
