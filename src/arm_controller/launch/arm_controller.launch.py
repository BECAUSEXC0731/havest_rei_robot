import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='/dev/ttyACM0'),
        Node(
            package='arm_controller',
            executable='arm_swiftpro',
            name='arm_controller',
            output='screen',
            parameters=[{'port': LaunchConfiguration('port')}]
        ),
    ])
