# fox_grape_harvest — 葡萄采摘功能包使用说明书

> 适用版本：ROS2 Humble
> 运行平台：Jetson Orin Nano / Ubuntu 22.04
> 硬件：Orbbec Astra Pro Plus、uArm Swift Pro、众灵总线舵机夹爪、三轮全向底盘
> 主节点：`grape_harvest_node`

---

## 文件结构

```
src/fox_grape_harvest/
├── package.xml / setup.py / setup.cfg
├── launch/
│   ├── grape_harvest.launch.py   # 只启动采摘节点
│   └── full_system.launch.py     # 导航、相机、机械臂、夹爪、采摘节点一键启动
├── config/
│   └── harvest_config.yaml       # 航点、相机、模型、工作空间和抓取参数
├── fox_grape_harvest/
│   ├── harvest_node.py           # ★ 主调度节点：状态机、命令、采摘流程
│   ├── yolo_detector.py          # YOLO .pt / .onnx 检测封装
│   ├── depth_utils.py            # 深度定位、手动 D2C、工作空间判定
│   ├── arm_interface.py          # 机械臂和夹爪服务封装
│   ├── chassis_interface.py      # Nav2 导航、底盘旋转微调
│   ├── wait_utils.py             # 长流程的 Future 等待和 executor 协调
│   └── grape_grasp_test.py       # 单颗抓取测试脚本入口
└── scripts/
    ├── grape_grasp_test.py       # ★ 交互式单颗抓取测试
    └── test_detection.py         # 检测和定位预览，不驱动机械臂
```

---

## 功能详细说明

### 1. 自动采摘流程

节点启动后默认处于待命状态，不会自动驱动车辆或机械臂。收到 `start` 命令后，流程如下：

1. 等待相机内参，然后让机械臂回到配置的安全位置。
2. 按 `waypoints` 顺序通过 Nav2 导航到每个航点。
3. 等待图像稳定，对多帧 RGB 图像运行 YOLO 检测。
4. 根据检测框中心、深度和手眼标定计算机器人坐标系下的葡萄位置。
5. 判断目标是否在机械臂工作空间内；满足抓取条件时，机械臂先到过渡点，再到抓取点，夹爪夹紧后把葡萄放到车载篮子。
6. 当前航点一颗也没抓到时，可按配置做底盘正反向角度扫描；仍没有可抓目标时，可尝试将最近的不可达目标夹取位置投影到工作空间边界内。
7. 航点全部完成后（若 `return_to_origin` 开启）导航回地图原点，并让机械臂归位。

底盘微调只做原地旋转，不能改变葡萄与底盘的距离。目标距离超出机械臂工作范围时，应调整航点或人工挪动车辆。

### 2. 深度定位与标定

定位链路为：RGB 检测框中心 → 深度取样（最近 7 帧中值）→ 相机 3D 坐标 → 手眼矩阵转换到机械臂基座坐标系（mm）→ 加工具偏移。

采摘前确认以下标定文件及相机设置：

| 文件 / 设置 | 用途 | 注意事项 |
|-------------|------|----------|
| `calib_result/hand_eye_result.json` | 相机到机械臂基座的 4×4 变换矩阵 | 必需；缺失时节点初始化失败 |
| `calib_result/color_ir_extrinsic.json` | 彩色相机到 IR/深度相机的外参 | 用于软件 D2C；缺失时按深度图与彩色图已对齐处理，定位可能偏差 |
| `calib_data/ir/ir_camera_info.yaml` | IR/深度相机内参 | 与 D2C 外参配套使用 |
| `calib_data/color/color_camera_info.yaml` | 彩色相机内参 | 启动相机时通过 `color_info_url` 加载；本项目标定值 `fx≈607` |
| `/camera/depth/image_raw` | 原始深度图 | Astra Pro 使用手动 D2C，订阅未对齐的原始深度数据 |

> **深度单位：** Astra Pro 的 `16UC1` 深度值单位为厘米，代码按 `/100` 转米，不是 `/1000`；`32FC1` 数据按米处理。修改深度转换逻辑前务必核实相机实际编码和单位。
>
> 相机 `camera_info` 由启动相机时指定的内参文件决定。内参与手眼标定不匹配会造成系统性定位偏差。

### 3. 编译

```bash
cd ~/ros2fox
source /opt/ros/humble/setup.zsh
colcon build --packages-select fox_grape_harvest
source install/setup.zsh
```

修改本包 Python 代码后必须重新构建，`ros2 run` 和 `ros2 launch` 执行的是安装空间中的版本。

### 4. 启动方式

#### 4.1 全系统启动

```bash
ros2 launch fox_grape_harvest full_system.launch.py
```

该 launch 会启动导航（含底盘、雷达、Nav2、RViz）、Orbbec 相机、机械臂、夹爪及采摘节点。相机默认使用本项目标定内参。

可传入的 launch 参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `open_rviz` | `true` | 是否启动 RViz |
| `config_file` | 包内 `config/harvest_config.yaml` | 采摘配置文件 |
| `color_info_url` | `file:///home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml` | 彩色相机内参 |
| `ir_info_url` | `file:///home/ubuntu/ros2fox/calib_data/ir/ir_camera_info.yaml` | IR/深度相机内参 |

例如：

```bash
ros2 launch fox_grape_harvest full_system.launch.py \
  open_rviz:=true \
  config_file:=/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml
```

#### 4.2 只启动采摘节点

先单独启动相机、机械臂、夹爪和导航，再运行：

```bash
ros2 launch fox_grape_harvest grape_harvest.launch.py \
  config_file:=/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml
```

也可以直接运行节点：

```bash
ros2 run fox_grape_harvest grape_harvest_node \
  --ros-args -p config_file:=/home/ubuntu/ros2fox/src/fox_grape_harvest/config/harvest_config.yaml
```

`harvest_config.yaml` 是普通 YAML，不是 ROS 参数文件；不要用 `--params-file` 加载，使用节点参数 `config_file` 指定路径。

### 5. 受控模式：命令与状态

#### 5.1 命令 `/grape_harvest/command`

类型：`std_msgs/msg/String`。支持 JSON 命令以及纯文本命令：

| 命令 | 参数 | 功能 |
|------|------|------|
| `start` | 无 | 按配置航点运行完整采摘流程 |
| `pick_one` | 必须提供 `x`,`y`,`z`（机器人坐标系 mm） | 只抓一颗，并优先抓离给定位置最近的检测目标 |
| `pause` | 无 | 在流程检查点暂停 |
| `resume` | 无 | 继续暂停的流程 |
| `stop` | 无 | 协作式停止，并请求取消当前 Nav2 目标 |
| `reload` | 无 | 重新读取配置中支持在线更新的抓取参数 |

命令行示例：

```bash
# 完整流程
ros2 topic pub --once /grape_harvest/command std_msgs/msg/String \
  'data: "{\"cmd\": \"start\"}"'

# 抓取离机器人坐标 (231, 178, 95) mm 最近的目标
ros2 topic pub --once /grape_harvest/command std_msgs/msg/String \
  'data: "{\"cmd\": \"pick_one\", \"x\": 231, \"y\": 178, \"z\": 95}"'

# 暂停、继续或停止
ros2 topic pub --once /grape_harvest/command std_msgs/msg/String 'data: "pause"'
ros2 topic pub --once /grape_harvest/command std_msgs/msg/String 'data: "resume"'
ros2 topic pub --once /grape_harvest/command std_msgs/msg/String 'data: "stop"'
```

JSON 命令必须作为字符串发送。不要省略外层引号，否则 ROS CLI 可能把 `{...}` 解析成 YAML 字典并转为非 JSON 字符串。
>
> **注意：** `pick_one` 必须提供完整且有效的 `x`,`y`,`z`。当前节点在坐标缺失或无法解析时会按完整采摘流程处理；为避免意外启动航点任务，不要省略坐标。

#### 5.2 状态 `/grape_harvest/status`

类型：`std_msgs/msg/String`，JSON 格式，每秒发布一次，状态变化时也会立即发布。

```bash
ros2 topic echo /grape_harvest/status
```

主要字段：`state`（`idle` / `running` / `paused` / `done` / `error`）、`stage`、`message`、`waypoint`、`waypoints`、`detected`、`picked`、`running`、`paused`、`elapsed_s`。

### 6. 配置文件说明

所有业务参数位于 [`config/harvest_config.yaml`](config/harvest_config.yaml)：

| 配置组 | 常用参数 | 说明 |
|--------|----------|------|
| 模型与相机 | `yolo_model_path`、`yolo_confidence`、`target_class`、`camera_*_topic` | YOLO 模型、目标类别及 RGB-D 话题 |
| 定位 | `hand_eye_calib_path`、`d2c_extrinsic_path`、`ir_camera_info_path` | 手眼标定和可选手动 D2C 文件 |
| 检测 | `image_settle_sec`、`detect_frames`、`detect_frame_interval_sec` | 到点稳定等待、多帧检测参数 |
| `arm` | `workspace_*`、`transition_*`、`tool_offset_*`、`home_*` | 工作空间（mm）、过渡点、工具补偿和安全归位点 |
| `arm.grasp_check` | `margin_*`、`marginal_mm`、`radius_*`、`grasp_marginal` | 可抓性判定容差；不改变视觉 3D 定位结果 |
| `arm` 兜底抓取 | `fallback_nearest`、`fallback_inward_mm` | 扫描失败后是否尝试最近可达点 |
| `chassis` | `rotate_*` | 原地旋转控制、扫描角度与稳定等待时间 |
| `navigation` | `use_nav2`、`nav_timeout` | Nav2 导航开关和超时；当前不支持关闭 Nav2 后的手动导航 |
| 航点 | `waypoints` | `map` 坐标系，位置单位米；按列表顺序执行 |
| 放篮与返航 | `car_basket`、`return_to_origin` | 车载篮子位置为机械臂坐标系 mm；是否返地图原点 |

工具偏移在机械臂局部坐标系中定义，抓取时会根据目标方向转换到机器人坐标系。应根据实际夹爪 TCP 测量并调整，不要将其与相机手眼标定混为一谈。

### 7. 独立测试工具

#### 7.1 `grape_grasp_test.py` — 交互式单颗抓取

```bash
ros2 run fox_grape_harvest grape_grasp_test.py
```

需要相机、机械臂和夹爪运行；该工具不执行 Nav2 导航。OpenCV 窗口中按空格抓取当前选中的可抓目标，按 `q` 或 `Esc` 退出。建议先用它验证标定和工具偏移，再运行完整流程。

#### 7.2 `test_detection.py` — 检测与定位预览

只做检测和深度定位，不驱动机械臂。本脚本没有注册为 `ros2 run` 可执行项，需在 ROS2 环境已加载时直接运行：

```bash
python3 src/fox_grape_harvest/scripts/test_detection.py \
  --model /home/ubuntu/ros2fox/models/grape.pt \
  --calib /home/ubuntu/ros2fox/calib_result/hand_eye_result.json \
  --conf 0.5
```

---

## 常用检查与调用示例

```bash
# 检查机械臂、夹爪服务
ros2 service list | grep -E 'goto_position|gripper/grip|^/home$'

# 检查相机图像和 Nav2 action
ros2 topic hz /camera/color/image_raw
ros2 topic hz /camera/depth/image_raw
ros2 action list | grep navigate_to_pose

# 查看节点命令与状态
ros2 topic echo /grape_harvest/command
ros2 topic echo /grape_harvest/status
```

命令话题可由命令行、WebUI 或其他 ROS2 节点使用。WebUI 的部分单颗抓取功能可能直接调用机械臂和夹爪服务，不一定经过本节点。

---

## 话题与服务

### 订阅的话题与动作

| 名称 | 类型 | 用途 |
|------|------|------|
| `/camera/color/image_raw` | `sensor_msgs/msg/Image` | 彩色图像和 YOLO 检测 |
| `/camera/depth/image_raw` | `sensor_msgs/msg/Image` | 原始深度图 |
| `/camera/color/camera_info` | `sensor_msgs/msg/CameraInfo` | 彩色相机内参 |
| `/odom` | `nav_msgs/msg/Odometry` | 底盘原地旋转的闭环反馈 |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | 航点导航 |
| `/grape_harvest/command` | `std_msgs/msg/String` | 采摘命令 |

相机话题使用 `qos_profile_sensor_data` 订阅，以兼容 Orbbec 的 BEST_EFFORT QoS。

### 发布的话题

| 名称 | 类型 | 用途 |
|------|------|------|
| `/grape_harvest/status` | `std_msgs/msg/String` | 采摘状态 JSON |
| `/grape_harvest/debug_image` | `sensor_msgs/msg/Image` | 带检测结果的调试图像 |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 底盘旋转微调 |

### 调用的服务

| 服务 | 类型 | 功能 |
|------|------|------|
| `/goto_position` | `arm_controller/srv/Move` | 移动机械臂到指定位置（mm） |
| `/home` | `std_srvs/srv/SetBool` | 使用机械臂驱动提供的归位位置 |
| `/gripper/grip` | `std_srvs/srv/SetBool` | 夹爪夹紧或松开 |

机械臂抓取坐标以机械臂基座为参考，单位为毫米；航点坐标以 `map` 为参考，单位为米。

---

## 执行程序一览

| 程序 | 类型 | 节点 / 入口 | 功能 |
|------|------|-------------|------|
| `grape_harvest_node` | Python | `grape_harvest_node` | 导航、检测、定位、抓取、放篮的主流程 |
| `grape_grasp_test.py` | Python | `grape_grasp_test` | 交互式单颗抓取测试 |
| `test_detection.py` | Python 脚本 | `grape_detection_test` | YOLO 检测和 3D 定位预览 |
| `grape_harvest.launch.py` | ROS 2 launch | — | 只启动采摘节点 |
| `full_system.launch.py` | ROS 2 launch | — | 启动采摘所需的完整系统 |

---

## 简介

本包负责 FOX 葡萄采摘机器人的主流程编排，连接 Nav2 导航、Orbbec RGB-D 相机、YOLO 检测、手眼标定定位、uArm 机械臂和夹爪。

```mermaid
graph LR
    A[Nav2 航点导航] --> B[RGB-D 相机]
    B --> C[YOLO 检测与深度定位]
    C --> D[工作空间判定]
    D --> E[机械臂与夹爪抓取]
    E --> F[车载篮子放置]
    G[命令与状态话题] --> H[采摘节点]
    H --> A
```

### 硬件与运行前提

- 相机、机械臂、夹爪、底盘和 Nav2 必须正常运行；启动后可用 `start` 命令启动完整流程。
- 需要可用的 YOLO 模型文件和手眼标定结果；模型不存在时节点会跳过检测，不能完成采摘。
- `stop` 是协作式停止，不是硬件急停；机械臂正在执行的动作可能会先完成。发生危险时使用设备的硬件急停或断电措施。
- `fallback_nearest` 可能把抓取点夹到目标附近的工作空间边缘，存在夹空或夹偏风险；现场使用前应充分验证并按需关闭。
- 采摘运行期间人员不得进入机械臂工作空间。
