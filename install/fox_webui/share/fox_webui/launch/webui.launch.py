"""FOX WebUI 启动文件。

用法:
  ros2 launch fox_webui webui.launch.py
  ros2 launch fox_webui webui.launch.py port:=8081 robot_name:=bot2
  ros2 launch fox_webui webui.launch.py config_file:=/path/to/my_webui.yaml

多机（模式 C 对称 HTTP 聚合，详见 docs/WebUI_技术文档.md §7.4）:
  # 每台机上跑一份，各自列出"另外几台"；任一台的 :8080 都能看到全部机器
  export ROS_LOCALHOST_ONLY=1          # ⚠️ 防串台，必须
  ros2 launch fox_webui webui.launch.py robot_name:=bot1 \
      peers:="bot2=http://192.168.1.12:8080,bot3=http://192.168.1.13:8080"

⚠️⚠️ 踩过的坑（2026-09-20 实测）：**参数文件必须是 ROS 参数格式**
--------------------------------------------------------------------------
    /**:                 ← 或具体节点名 /fox_webui_agent
      ros__parameters:
        port: 8080

若像普通配置文件那样在顶层直接写 `port: 8080`，节点会在启动瞬间挂掉：

    rclpy._rclpy_pybind11.RCLError: failed to initialize rcl:
    Couldn't parse params file: '.../config/webui.yaml'.
    Error: Cannot have a value before ros__parameters at line 7

config/webui.yaml 已经是正确格式；自定义参数文件也必须照这个写。
（之前一直用 scripts/dev_restart.sh 直接跑可执行文件、不经参数文件，
  所以这个坑直到用 launch 启动才暴露出来。）
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _agent_node(context, *args, **kwargs):
    """按“参数文件兜底 + 显式命令行覆盖”组装节点。"""
    params = [LaunchConfiguration('config_file').perform(context)]

    overrides = {}
    port = str(LaunchConfiguration('port').perform(context)).strip()
    if port:
        overrides['port'] = int(port)          # 参数文件里是 int，保持一致
    for name in ('host', 'robot_name', 'peers'):
        val = str(LaunchConfiguration(name).perform(context)).strip()
        if val:
            overrides[name] = val
    for name in ('peer_hz', 'peer_timeout'):
        val = str(LaunchConfiguration(name).perform(context)).strip()
        if val:
            overrides[name] = float(val)
    if overrides:
        params.append(overrides)               # 覆盖参数文件里的值

    return [Node(
        package='fox_webui',
        executable='fox_webui_agent',
        name='fox_webui_agent',
        output='screen',
        emulate_tty=True,
        parameters=params,
    )]


def generate_launch_description():
    pkg = get_package_share_directory('fox_webui')
    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=os.path.join(pkg, 'config', 'webui.yaml'),
            description='WebUI 参数文件（必须是 ROS 参数格式，见文件头说明）'),
        # 下面三个默认留空 = 用参数文件里的值；显式传入才覆盖
        DeclareLaunchArgument('port', default_value='',
                              description='覆盖监听端口，如 port:=8081'),
        DeclareLaunchArgument('host', default_value='',
                              description='覆盖监听地址，如 host:=127.0.0.1'),
        DeclareLaunchArgument('robot_name', default_value='',
                              description='覆盖机器人名（多机时区分）'),
        # ── 多机（模式 C 对称 HTTP 聚合）；留空 = 用参数文件里的值 / 单机 ──
        DeclareLaunchArgument('peers', default_value='',
                              description='邻居名单 "bot2=http://ip:8080,bot3=http://…"（逗号分隔，不写自己）'),
        DeclareLaunchArgument('peer_hz', default_value='',
                              description='邻居状态拉取频率（Hz），默认 5.0'),
        DeclareLaunchArgument('peer_timeout', default_value='',
                              description='单次 HTTP 超时（秒），默认 1.0'),

        OpaqueFunction(function=_agent_node),
    ])
