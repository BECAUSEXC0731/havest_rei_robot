from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace
from launch.actions import GroupAction
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import Node
import os


def generate_launch_description():
    # Declare arguments
    args = [
        DeclareLaunchArgument('camera_name', default_value='camera'),
        # ⚠️ depth_registration 暂保持 false：
        #   Astra Pro (0x0403) + SDK 1.10.35 的 D2C 对齐会崩溃
        #   （Can not find matched camera param / 深度内参 NaN）
        #   待换 SDK 版本或改用手动对齐后再置 true。
        DeclareLaunchArgument('depth_registration', default_value='false'),
        DeclareLaunchArgument('serial_number', default_value=''),
        DeclareLaunchArgument('usb_port', default_value=''),
        DeclareLaunchArgument('device_num', default_value='1'),
        DeclareLaunchArgument('vendor_id', default_value='0x2bc5'),
        DeclareLaunchArgument('product_id', default_value=''),
        DeclareLaunchArgument('enable_point_cloud', default_value='true'),
        DeclareLaunchArgument('enable_colored_point_cloud', default_value='false'),
        DeclareLaunchArgument('cloud_frame_id', default_value=''),
        DeclareLaunchArgument('point_cloud_qos', default_value='default'),
        DeclareLaunchArgument('connection_delay', default_value='100'),
        DeclareLaunchArgument('color_width', default_value='640'),
        DeclareLaunchArgument('color_height', default_value='480'),
        DeclareLaunchArgument('color_fps', default_value='30'),
        DeclareLaunchArgument('color_format', default_value='RGB'),
        DeclareLaunchArgument('enable_color', default_value='true'),
        DeclareLaunchArgument('flip_color', default_value='false'),
        DeclareLaunchArgument('color_qos', default_value='default'),
        DeclareLaunchArgument('color_camera_info_qos', default_value='default'),
        DeclareLaunchArgument('enable_color_auto_exposure', default_value='true'),
        DeclareLaunchArgument('color_exposure', default_value='-1'),
        DeclareLaunchArgument('color_gain', default_value='-1'),
        DeclareLaunchArgument('enable_color_auto_white_balance', default_value='true'),
        DeclareLaunchArgument('color_white_balance', default_value='-1'),
        DeclareLaunchArgument('depth_width', default_value='640'),
        DeclareLaunchArgument('depth_height', default_value='480'),
        DeclareLaunchArgument('depth_fps', default_value='30'),
        DeclareLaunchArgument('depth_format', default_value='Y11'),
        DeclareLaunchArgument('enable_depth', default_value='true'),
        DeclareLaunchArgument('flip_depth', default_value='false'),
        DeclareLaunchArgument('depth_qos', default_value='default'),
        DeclareLaunchArgument('depth_camera_info_qos', default_value='default'),
        DeclareLaunchArgument('ir_width', default_value='640'),
        DeclareLaunchArgument('ir_height', default_value='480'),
        DeclareLaunchArgument('ir_fps', default_value='30'),
        DeclareLaunchArgument('ir_format', default_value='Y10'),
        DeclareLaunchArgument('enable_ir', default_value='true'),
        DeclareLaunchArgument('flip_ir', default_value='false'),
        DeclareLaunchArgument('ir_qos', default_value='default'),
        DeclareLaunchArgument('ir_camera_info_qos', default_value='default'),
        DeclareLaunchArgument('ir_exposure', default_value='-1'),
        DeclareLaunchArgument('ir_gain', default_value='-1'),
        DeclareLaunchArgument('publish_tf', default_value='true'),
        DeclareLaunchArgument('tf_publish_rate', default_value='0.0'),
        DeclareLaunchArgument('ir_info_url', default_value=''),
        DeclareLaunchArgument('color_info_url', default_value=''),
        DeclareLaunchArgument('log_level', default_value='none'),
        DeclareLaunchArgument('enable_publish_extrinsic', default_value='false'),
        DeclareLaunchArgument('enable_d2c_viewer', default_value='false'),
        # Astra Pro (0x0403) 不支持 LDP / 激光能量调节，此项无效但保留参数位
        DeclareLaunchArgument('enable_ldp', default_value='false'),
        # 软滤波会滤除孤立/稀疏深度点，远处葡萄区域点稀疏最易被滤掉。
        # 默认关闭以保留远处深度；如需降噪可改回 true 并调 soft_filter_speckle_size（默认 480）
        DeclareLaunchArgument('enable_soft_filter', default_value='false'),
        DeclareLaunchArgument('soft_filter_max_diff', default_value='-1'),
        DeclareLaunchArgument('soft_filter_speckle_size', default_value='-1'),
        # ── 深度后处理滤波参数（可用 ros2 param set 或启动时调，边看 depth_viewer 边调）──
        # 降噪滤波(NoiseRemoval)：默认 true，会删掉葡萄这类孤立/稀疏的深度点 → 必须关
        DeclareLaunchArgument('enable_noise_removal_filter', default_value='false'),
        # 若想保留降噪，这两个是"强度"：
        #   noise_removal_filter_max_size = 被删除连通块的最大像素数（默认 80），越小删得越少
        #   noise_removal_filter_min_diff  = 深度差阈值（默认 256），越小越敏感
        DeclareLaunchArgument('noise_removal_filter_max_size', default_value='80'),
        DeclareLaunchArgument('noise_removal_filter_min_diff', default_value='256'),
        # 降采样(Decimation)：scale 越大分辨率越低、深度点越稀（默认关闭）
        DeclareLaunchArgument('enable_decimation_filter', default_value='false'),
        DeclareLaunchArgument('decimation_filter_scale', default_value='-1'),
        # HDR / 序列滤波（默认关闭）
        DeclareLaunchArgument('enable_hdr_merge', default_value='false'),
        DeclareLaunchArgument('enable_sequence_id_filter', default_value='false'),
        # 孔洞填充(HoleFilling)：默认 false，打开可把葡萄上的零星空洞补上
        DeclareLaunchArgument('enable_hole_filling_filter', default_value='true'),
        DeclareLaunchArgument('hole_filling_filter_mode', default_value='fill_all'),
        # 空间/时间平滑：实测时间平滑对深色葡萄反而会"粘住"旧值/拖影，先关闭
        # 葡萄闪烁靠抓取代码端"多帧中值采样"解决，比相机滤波更可控
        DeclareLaunchArgument('enable_spatial_filter', default_value='false'),
        DeclareLaunchArgument('enable_temporal_filter', default_value='false'),
        # 时间平滑参数（-1 用SDK默认）：diff_threshold 越小越敏感；weight 越大越平滑但延迟越高
        DeclareLaunchArgument('temporal_filter_diff_threshold', default_value='-1'),
        DeclareLaunchArgument('temporal_filter_weight', default_value='-1'),
        # 空间平滑参数（-1 用SDK默认）
        DeclareLaunchArgument('spatial_filter_alpha', default_value='-1'),
        DeclareLaunchArgument('spatial_filter_magnitude', default_value='-1'),
        DeclareLaunchArgument('spatial_filter_radius', default_value='-1'),
        DeclareLaunchArgument('spatial_filter_diff_threshold', default_value='-1'),
        # 深度范围阈值：0 表示不启用。若只要 0.2~2m，可设 threshold_filter_min=200 / max=2000 (mm)
        DeclareLaunchArgument('threshold_filter_min', default_value='0'),
        DeclareLaunchArgument('threshold_filter_max', default_value='0'),
        DeclareLaunchArgument('ordered_pc', default_value='false'),
        DeclareLaunchArgument('enable_depth_scale', default_value='true'),
        # Astra Pro 不支持硬件对齐(ALIGN_D2C_HW)，需用软件对齐(SW)，否则启动崩溃
        DeclareLaunchArgument('align_mode', default_value='SW'),
        DeclareLaunchArgument('laser_energy_level', default_value='-1'),
        DeclareLaunchArgument('enable_heartbeat', default_value='false'),
    ]

    # Node configuration
    parameters = [{arg.name: LaunchConfiguration(arg.name)} for arg in args]
    # get  ROS_DISTRO
    ros_distro = os.environ["ROS_DISTRO"]
    if ros_distro == "foxy":
        return LaunchDescription(
            args
            + [
                Node(
                    package="orbbec_camera",
                    executable="orbbec_camera_node",
                    name="ob_camera_node",
                    namespace=LaunchConfiguration("camera_name"),
                    parameters=parameters,
                    output="screen",
                )
            ]
        )
    # Define the ComposableNode
    else:
        # Define the ComposableNode
        compose_node = ComposableNode(
            package="orbbec_camera",
            plugin="orbbec_camera::OBCameraNodeDriver",
            name=LaunchConfiguration("camera_name"),
            namespace="",
            parameters=parameters,
        )
        # Define the ComposableNodeContainer
        container = ComposableNodeContainer(
            name="camera_container",
            namespace="",
            package="rclcpp_components",
            executable="component_container",
            composable_node_descriptions=[
                compose_node,
            ],
            output="screen",
        )
        # Launch description
        ld = LaunchDescription(
            args
            + [
                GroupAction(
                    [PushRosNamespace(LaunchConfiguration("camera_name")), container]
                )
            ]
        )
        return ld
