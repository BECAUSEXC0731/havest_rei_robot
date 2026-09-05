# AGENTS.md — ros2fox 项目指南

面向 AI 编码代理的 ROS2 机器人项目工作指南。完整硬件规格、服务/话题接口与标定流程见 [README.md](README.md)；系统启动顺序见根目录 [`启动`](启动) 文件。

## 项目概览

ROS2 **Humble** + Jetson Orin Nano (Ubuntu 22.04) 的葡萄采摘机器人：
YOLO 视觉检测 + 机械臂 (uArm Swift Pro) + 三轮全向底盘 + Orbbec Astra Pro Plus 深度相机 + Cartographer 建图 / Nav2 导航 + 众灵总线舵机夹爪。

## 构建与运行

```bash
# 构建单个包（修改代码后必须重编！）
cd ~/ros2fox && colcon build --packages-select <包名>

# 环境变量（用 zsh；bash 里 source setup.bash 会报 BASH_SOURCE 错误）
source /opt/ros/humble/setup.zsh
source ~/ros2fox/install/setup.zsh
```

> ⚠️ **改 src 下 Python 脚本后 `ros2 run` 不会自动生效**：ament_cmake 包会把 `scripts/` 安装到 `install/<pkg>/lib/<pkg>/`，必须 `colcon build --packages-select <pkg>`（或手动同步 install 副本）。这是本项目最常踩的坑。

## 包结构与职责

| 包 | 类型 | 职责 | 文档 |
|----|------|------|------|
| `arm_controller` | ament_cmake | uArm Swift Pro 机械臂驱动 + 手眼标定/抓取脚本 | [README](src/arm_controller/README.md) |
| `fox_grape_harvest` | ament_python | 主流程：导航→YOLO 检测→深度定位→机械臂抓取 | 见下 |
| `fox_navigation_ros2` | ament_cmake | 导航包（地图+AMCL+Nav2 一键启动，含诊断脚本） | [README](src/fox_navigation_ros2/README.md)、[导航测试指南](src/fox_navigation_ros2/导航测试指南.md) |
| `fox_slam_ros2` | ament_cmake | Cartographer 建图 + 雷达参数 | [README](src/fox_slam_ros2/README.md)、[CARTOGRAPHER_SWITCH](src/fox_slam_ros2/CARTOGRAPHER_SWITCH.md) |
| `gripper_control` | ament_cmake | 众灵总线舵机夹爪 | [说明](src/gripper_control/说明.md) |
| `rei_robot_base` | ament_cmake | 三轮全向底盘驱动 | [README](src/rei_robot_base/README.md) |
| `ydlidar_ros2_driver` | ament_cmake | 激光雷达驱动 | [README](src/ydlidar_ros2_driver/README.md) |
| `calibration` | 纯 Python（非 ROS2 包） | 相机内参/外参标定工具 | 用 `python3 src/calibration/...` 直接运行 |
| `fox_description_ros2` / `OrbbecSDK_ROS2` | 模型 / 相机驱动 | URDF 描述 / Orbbec 相机 | — |

### fox_grape_harvest 内部结构
- `fox_grape_harvest/harvest_node.py` — 主节点（导航→检测→抓取状态机）
- `fox_grape_harvest/yolo_detector.py` — YOLO 检测（模型 `models/grape.pt`，未训练）
- `fox_grape_harvest/depth_utils.py` — 深度定位（像素→相机3D→机器人系）
- `fox_grape_harvest/arm_interface.py` / `chassis_interface.py` — 机械臂 / 底盘接口
- `config/harvest_config.yaml` — 所有可调参数（工作空间、工具偏移 tool_offset_*、航点、相机话题）
- `scripts/grape_grasp_test.py`、`test_detection.py` — 独立测试脚本

## 关键约定与陷阱（重要，改动前必读）

1. **深度话题单位是厘米(cm)，不是毫米**。16UC1 深度数据转米是 `/100`（不是 `/1000`）。改任何深度换算代码务必核对。
2. **手眼标定**：机械臂实际只用 3 轴（手腕轴未连接标定板），`p_local` 偏移模型不可用。正确做法：ArUco 标记 (DICT_4X4_100, ID=4, 50mm) 贴末端中心 → `hand_eye_calib.py`。结果存 `calib_result/hand_eye_result.json`。
3. **彩色内参以 `calib_data/color/color_camera_info.yaml` 为准 (fx≈607)**；根 README 的 fx=474 已过时。相机内参决定手眼标定与像素→3D，重做标定前必须先用正确内参启动相机 (`color_info_url:=file://.../color_camera_info.yaml`)。
4. **雷达建图/导航配置必须一致**：都使用 `fox_slam_ros2/config/fox_lidar_params.yaml`（front_lidar_link + inverted=true）。ydlidar 报 "Unknown error" = 端口被占用，先 `pkill` 残留 ydlidar 进程。
5. **深度对齐**：Astra Pro 硬件 D2C 会崩溃，用手动 D2C（`calibrate_color_ir.py` 生成 `calib_result/color_ir_extrinsic.json`，抓取时自动使用）。
6. **Nav2 (Humble 版插件名)**：AMCL 必须用 `nav2_amcl::OmniMotionModel`（Humble 无 OmniDiffTurnHeuristic）；DWB 控制器插件名 `dwb_core::DWBLocalPlanner` 且必须配 critics（插件名带 `Critic` 后缀）；local costmap 需 `always_send_full_costmap: true` 才会发全量话题。见 `param/nav2_params.yaml`。
7. **夹爪**：端口 `/dev/ttyGripper`（udev 软链接，CH340 芯片，节点名 ttyCH341USB*）；众灵协议；实测 **2000=抓紧、500=松开**（与常规舵机习惯相反）。
8. **标定板规格**：棋盘格 4x6 内角点、29mm/格。`calibrate_camera.py` 默认 8x6，需显式 `--size 4x6 --square 29`。
9. **ROS1 遗留**：`arm_controller/src/` 下带 `ros/ros.h` 的 4 个 .cpp 未编译，忽略即可。

## 设备与端口

| 设备 | 端口 | 说明 |
|------|------|------|
| 机械臂 | `/dev/ttyACM0` | 115200，G-code 协议 |
| 底盘 | `/dev/ttyUSB1` | 启动需 `export REI_ROBOT=fox_three` |
| 雷达 | `/dev/ydlidar` (ttyUSB0) | CP210x |
| 夹爪 | `/dev/ttyGripper` | 众灵总线舵机，115200 |
