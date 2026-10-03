from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'map_file',
            default_value='map.yaml',
            description='Map file name'
        ),
        DeclareLaunchArgument(
            'map_directory',
            default_value=EnvironmentVariable('MAP_DIRECTORY', default_value='.'),
            description='Map save directory'
        ),

        Node(
            package='nav2_map_server',
            executable='map_saver_cli',
            name='map_saver',
            arguments=['-f',
                       PathJoinSubstitution([LaunchConfiguration('map_directory'),
                                             LaunchConfiguration('map_file')])],
            output='screen'
        ),
    ])
