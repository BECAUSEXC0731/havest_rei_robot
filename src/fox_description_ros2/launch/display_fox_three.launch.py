import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_dir = get_package_share_directory('fox_description')
    xacro_file = os.path.join(pkg_dir, 'xacro', 'fox.xacro')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'urdf.rviz')

    robot_description = ParameterValue(
        Command(['xacro', ' ', xacro_file, ' type:=three sim:=0']),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument('open_rviz', default_value='false'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('open_rviz'))
        ),
    ])
