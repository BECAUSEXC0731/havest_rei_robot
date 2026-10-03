import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'map_file',
            default_value='map.yaml',
            description='Map YAML file name'
        ),
        DeclareLaunchArgument(
            'map_directory',
            default_value=EnvironmentVariable('MAP_DIRECTORY', default_value='.'),
            description='Map directory path'
        ),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{
                'yaml_filename':
                    PathJoinSubstitution([LaunchConfiguration('map_directory'),
                                          LaunchConfiguration('map_file')])
            }],
            output='screen'
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map_server',
            output='screen',
            parameters=[{
                'autostart': True,
                'node_names': ['map_server']
            }]
        ),
    ])
