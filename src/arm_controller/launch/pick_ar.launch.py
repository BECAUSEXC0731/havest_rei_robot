from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    arm_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(get_package_share_directory('arm_controller'), 'launch', 'arm_controller.launch.py')
        )
    )
    return LaunchDescription([
        arm_launch,
        Node(
            package='arm_controller',
            executable='pick_ar',
            name='pick_ar',
            output='screen'
        ),
    ])
