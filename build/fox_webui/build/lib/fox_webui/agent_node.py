"""每台机器人上的 WebUI Agent 进程（S1 版本：只读状态可视化）。

结构
----
  主线程        : uvicorn（FastAPI：HTTP / SSE / 静态页面）
  后台线程      : rclpy MultiThreadedExecutor（订阅话题 + TF 监听）

用法
----
    ros2 run fox_webui fox_webui_agent --ros-args -p port:=8080 -p robot_name:=bot1
    ros2 launch fox_webui webui.launch.py port:=8080

浏览器打开： http://<Jetson-IP>:8080
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time

import rclpy
from rclpy.executors import MultiThreadedExecutor

from fox_webui.state import StateStore, StateCollector
from fox_webui.webapi import create_app
from fox_webui.video import VideoBroker
from fox_webui.mapdata import MapData, DEFAULT_MAP_YAML
from fox_webui.control import ControlManager
from fox_webui.process_manager import ProcessManager, DEFAULT_MODULES_YAML
from fox_webui.peers import parse_peers, PeerAggregator

# ⚠️ 不要在这里 import PreviewDetector：它会把 fox_grape_harvest → ultralytics/torch
#    一起拉进来（本机实测 ~30-40s）。启动时先做端口检查、再用时再 import，
#    这样"端口被占用"能在 1-2s 内快速报错，不用先等 40s 才崩。
DEFAULT_HARVEST_CFG = '/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml'


def port_conflict(host: str, port: int) -> str | None:
    """端口预检：被占用就返回原因，否则返回 None。

    为什么自己做：不检查的话，节点会先花几十秒加载模型，最后才死在 uvicorn 的
        ERROR: [Errno 98] address already in use
        terminate called without an active exception   （退出码 -6/SIGABRT）
    而且报错里看不出"该怎么办"。
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind((host or '0.0.0.0', int(port)))
    except OSError as exc:
        return str(exc)
    finally:
        probe.close()
    return None


def _port_owner(port: int) -> str:
    """尽量找出占着端口的进程名（不依赖 ss/lsof 是否安装）。"""
    import glob
    out = []
    for d in glob.glob('/proc/[0-9]*'):
        try:
            pid = d.split('/')[-1]
            cmd = open(d + '/cmdline', 'rb').read().decode(errors='replace').replace('\0', ' ').strip()
        except Exception:
            continue
        if cmd and ('agent' in cmd or 'serv' in cmd or 'python' in cmd):
            out.append(f'{pid} {cmd[:80]}')
    return '；'.join(out[:3])


def lan_ip() -> str:
    """取本机在局域网中的 IP（不会真的发包）。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


def resolve_web_dir(explicit: str | None = None) -> str:
    """定位前端静态目录：参数 > install/share > 源码目录（便于开发调试）。"""
    if explicit and os.path.isdir(explicit):
        return explicit
    try:
        from ament_index_python.packages import get_package_share_directory
        cand = os.path.join(get_package_share_directory('fox_webui'), 'web')
        if os.path.isdir(cand):
            return cand
    except Exception:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, '..', 'web'))


def main(argv=None):
    rclpy.init(args=argv)
    node = rclpy.create_node('fox_webui_agent')
    node.declare_parameter('port', 8080)
    node.declare_parameter('host', '0.0.0.0')
    node.declare_parameter('robot_name', 'fox')
    node.declare_parameter('web_dir', '')
    node.declare_parameter('log_buffer', 500)
    node.declare_parameter('online_timeout', 3.0)
    node.declare_parameter('gripper_open_pulse', 500)     # 实测: 500 = 松开
    node.declare_parameter('gripper_close_pulse', 2000)   # 实测: 2000 = 抓紧
    node.declare_parameter('map_frame', 'map')
    node.declare_parameter('base_frame', 'base_footprint')
    node.declare_parameter('laser_frame', 'front_lidar_link')
    # 视频 / 地图 / 识别
    node.declare_parameter('video_fps', 10.0)
    node.declare_parameter('video_quality', 70)
    node.declare_parameter('map_yaml', DEFAULT_MAP_YAML)
    node.declare_parameter('detect_mode', 'yolo')      # yolo | sim
    node.declare_parameter('detect_hz', 3.0)
    node.declare_parameter('harvest_config', DEFAULT_HARVEST_CFG)
    node.declare_parameter('detect_on_start', False)   # 默认不开识别（吃 CPU/GPU）
    # 控制类
    node.declare_parameter('max_vx', 0.3)
    node.declare_parameter('max_vy', 0.3)
    node.declare_parameter('max_vth', 0.5)
    # 速度指令看门狗超时（秒）：前端 10Hz 续期，超过这么久没续期就自动归零。
    # ⚠️ 不要设得太小：实测端到端延迟已达 ~300 ms，300 ms 的阈值会让车"一动一停"
    #    （表现为"按住好几秒才有反应"），详见 control.py 里的实测说明。
    node.declare_parameter('cmd_timeout', 0.8)
    node.declare_parameter('nav_home_x', 0.0)
    node.declare_parameter('nav_home_y', 0.0)
    # 模块启停
    node.declare_parameter('modules_yaml', DEFAULT_MODULES_YAML)
    node.declare_parameter('enable_modules', True)
    # 多机（模式 C 对称 HTTP 聚合）：邻居名单 "bot2=http://192.168.1.12:8080,bot3=http://…"
    # 留空 = 单机（行为与从前完全一致）
    node.declare_parameter('peers', '')
    node.declare_parameter('peer_hz', 5.0)
    node.declare_parameter('peer_timeout', 1.0)

    p = lambda name: node.get_parameter(name).value
    port = int(p('port'))
    host = str(p('host'))
    robot_name = str(p('robot_name'))

    # ── 端口预检（快速失败；否则要等模型加载完才死在 uvicorn）──
    why = port_conflict(host, port)
    if why:
        owner = _port_owner(port)
        print('\n' + '=' * 66, flush=True)
        print(f'❌ 端口 {port} 已被占用，WebUI 无法启动：{why}', flush=True)
        if owner:
            print(f'   占用者可能是：{owner}', flush=True)
        print('   处理办法（任选一个）：', flush=True)
        print(f'     1) 停掉旧实例：  pkill -f "fox_webui_[a]gent"', flush=True)
        print(f'     2) 换个端口：    ros2 launch fox_webui webui.launch.py port:={port + 1}', flush=True)
        print('=' * 66 + '\n', flush=True)
        node.get_logger().error(f'端口 {port} 已被占用，退出。')
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()
        return 1

    store = StateStore(robot_name=robot_name,
                       log_buffer=int(p('log_buffer')),
                       online_timeout=float(p('online_timeout')))
    store.set_gripper_pulse_range(int(p('gripper_open_pulse')),
                                 int(p('gripper_close_pulse')))

    collector = StateCollector(node, store,
                               map_frame=str(p('map_frame')),
                               base_frame=str(p('base_frame')),
                               laser_frame=str(p('laser_frame')))

    # ── 视频（按需 MJPEG）/ 识别预览（按需 3Hz）/ 地图 ──
    # 重依赖（ultralytics/torch）在这里才 import，见文件头说明
    from fox_webui.preview_detector import PreviewDetector
    detector = PreviewDetector(node, store,
                               config_path=str(p('harvest_config')),
                               mode=str(p('detect_mode')),
                               hz=float(p('detect_hz')))
    broker = VideoBroker(node, store, detector=detector,
                         fps=float(p('video_fps')),
                         quality=int(p('video_quality')))
    mapdata = MapData(str(p('map_yaml')))
    control = ControlManager(node, store,
                             config_path=str(p('harvest_config')),
                             webui_cfg={'max_vx': float(p('max_vx')),
                                        'max_vy': float(p('max_vy')),
                                        'max_vth': float(p('max_vth')),
                                        'cmd_timeout': float(p('cmd_timeout')),
                                        'nav_home_x': float(p('nav_home_x')),
                                        'nav_home_y': float(p('nav_home_y'))})
    if bool(p('detect_on_start')):
        detector.acquire()                      # 常开模式（调试用）

    # ── 模块启停（白名单 + 进程组；不碰 rclpy 实体，只读 store 快照）──
    modules = None
    if bool(p('enable_modules')):
        try:
            modules = ProcessManager(store, yaml_path=str(p('modules_yaml')), node=node)
        except Exception as exc:
            node.get_logger().warn(f'模块启停不可用（配置读取失败）: {exc}')

    # ── 模式 C：邻居聚合（对称 HTTP）──
    # 纯 HTTP daemon 线程，**绝不碰 rclpy**；peers 为空时不起线程、无任何副作用。
    peer_list = parse_peers(str(p('peers')), me=robot_name)
    peers_agg = PeerAggregator(robot_name, peer_list, store,
                               hz=float(p('peer_hz')),
                               timeout=float(p('peer_timeout')))
    peers_agg.start()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, name='rclpy-spin', daemon=True)
    spin_thread.start()

    web_dir = resolve_web_dir(str(p('web_dir')) or None)
    app = create_app(store, web_dir=web_dir,
                     broker=broker, mapdata=mapdata, control=control,
                     modules=modules,
                     peers=peers_agg,
                     extra_status=lambda: {'detector': detector.status(),
                                           'control': control.status(),
                                           'peers': peers_agg.status(),
                                           'modules': (modules.status()['modules']
                                                       if modules is not None else {})})

    log = node.get_logger()
    log.info('=' * 62)
    log.info(f'🍇 FOX WebUI Agent 已启动  robot={robot_name}')
    log.info(f'   本机访问: http://127.0.0.1:{port}')
    log.info(f'   手机访问: http://{lan_ip()}:{port}')
    log.info(f'   前端目录: {web_dir}')
    log.info(f'   地图: {mapdata.meta().get("yaml")} (ok={mapdata.meta().get("ok")})')
    log.info(f'   识别预览: mode={detector.mode} {detector.hz:.1f}Hz 按需启用')
    log.info(f'   模块启停: {"可用 " + str(len(modules.names())) + " 个模块" if modules else "未启用"}')
    if peer_list:
        log.info(f'   多机(模式C): 邻居 ' + ', '.join(
            f'{x["name"]}→{x["url"]}' for x in peer_list))
        log.info('   ⚠️ 防串台：本机必须 export ROS_LOCALHOST_ONLY=1（跨机只走 HTTP）')
    else:
        log.info('   多机(模式C): 未启用（单机模式；peers 参数为空）')
    log.info('=' * 62)

    # 启动横幅（方便现场直接照抄地址）
    print('\n' + '=' * 62)
    print(f'  FOX WebUI  →  http://{lan_ip()}:{port}   (robot: {robot_name})')
    print('=' * 62 + '\n', flush=True)

    try:
        import uvicorn
        uvicorn.run(app, host=host, port=port, log_level='info', access_log=False)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            executor.shutdown(timeout_sec=2.0)
        except Exception:
            pass
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
