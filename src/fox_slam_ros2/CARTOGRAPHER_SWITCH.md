# Fox SLAM 算法切换记录（SLAM Toolbox → Cartographer）

> 记录时间：2026-08-01
> 目标：将建图算法从 **SLAM Toolbox**（Karto 图优化）切换为 **Cartographer**（Google 图优化 SLAM），
> 以利用其**子图（submap）+ 实时回环检测**能力，提高大场景建图精度。

---

## 1. 环境信息

| 项目 | 值 |
|------|-----|
| 系统 | Ubuntu 22.04（jammy） |
| ROS 版本 | ROS2 Humble |
| 架构 | arm64（Jetson 类） |
| 建图输入 | ydlidar 2D LaserScan `/scan`（0.1~6.0 m，10 Hz） |
| 里程计 | 底盘驱动发布 `/odom`（50 Hz）+ TF `odom→base_footprint` |
| IMU | 无 |

**坐标系链**（TF 树）：

```
map ──(Cartographer 发布)──> odom ──(底盘驱动发布)──> base_footprint ──(robot_state_publisher)──> front_lidar_link
```

---

## 2. 新旧方案对比

| 方案 | 包/节点 | 配置文件 | 类型 |
|------|---------|----------|------|
| 旧（SLAM Toolbox） | `slam_toolbox` / `async_slam_toolbox_node` | `config/fox_slam_params.yaml` + `launch/fox_slam.launch.py` | 图优化（Karto），带回环 |
| 新（Cartographer） | `cartographer_ros` / `cartographer_node` | `config/cartographer_fox.lua` + `launch/cartographer.launch.py` | 图优化（子图 + 分支定界回环） |

两个方案的文件均保留，可随时切换。

---

## 3. 切换流程

### 3.1 安装依赖

```bash
sudo apt-get update
sudo apt-get install -y ros-humble-cartographer ros-humble-cartographer-ros
```

> 安装后出现两个可执行节点：`cartographer_node`（核心 SLAM）和 `cartographer_occupancy_grid_node`（发布 `/map` 栅格地图，供 `map_saver` 存图）。

### 3.2 新增配置文件 `config/cartographer_fox.lua`

核心参数（适配本机）：

```lua
options = {
  map_frame = "map",
  tracking_frame = "base_footprint",   -- 机器人体坐标系
  published_frame = "odom",            -- Cartographer 发布 map→odom
  odom_frame = "odom",
  provide_odom_frame = false,          -- 底盘驱动已发布 odom→base_footprint，必须为 false 避免 TF 冲突
  use_pose_extrapolator = true,
  use_odometry = true,                 -- 使用底盘 /odom 里程计做运动预测
  num_laser_scans = 1,                 -- /scan 2D 激光
  ...
}
MAP_BUILDER.use_trajectory_builder_2d = true
TRAJECTORY_BUILDER_2D.use_imu_data = false               -- 无 IMU
TRAJECTORY_BUILDER_2D.min_range = 0.1                    -- 匹配雷达 range_min
TRAJECTORY_BUILDER_2D.max_range = 6.0                    -- 匹配雷达 range_max
TRAJECTORY_BUILDER_2D.submaps.grid_options_2d.resolution = 0.05
POSE_GRAPH.optimize_every_n_nodes = 90                   -- 回环全局优化频率
POSE_GRAPH.constraint_builder.min_score = 0.65           -- 回环匹配最低分数
...
return options                                          -- ★ 末尾必须有
```

### 3.3 新增 launch 文件 `launch/cartographer.launch.py`

结构与原 `fox_slam.launch.py` 一致（机器人模型、底盘、雷达、RViz 均复用），仅替换 SLAM 部分：

- `cartographer_node`：核心节点，传 `-configuration_directory` 与 `-configuration_basename`
- `cartographer_occupancy_grid_node`：发布 `/map`（`resolution=0.05`）
- **关键 remap**：`remappings=[('odometry', '/odom')]` —— Cartographer 内部订阅话题名是 `odometry`，需映射到底盘实际发布的 `/odom`

### 3.4 更新依赖声明 `package.xml`

```xml
<exec_depend>cartographer_ros</exec_depend>
```

（`CMakeLists.txt` 已整体安装 `config/` 与 `launch/` 目录，无需改动。）

### 3.5 更新启动脚本 `启动`

```diff
- 启动建图
- ros2 launch fox_slam_ros2 fox_slam.launch.py
+ 启动建图（Cartographer）
+ ros2 launch fox_slam_ros2 cartographer.launch.py
```

### 3.6 编译与验证

```bash
colcon build --packages-select fox_slam_ros2
```

验证命令（不连硬件）：
```bash
# 1) 验证 lua 配置能被加载（无 "Check failed" 即成功）
timeout 6 ros2 run cartographer_ros cartographer_node \
  -configuration_directory install/fox_slam_ros2/share/fox_slam_ros2/config \
  -configuration_basename cartographer_fox.lua

# 2) 验证 launch 可解析
ros2 launch fox_slam_ros2 cartographer.launch.py --show-args
```

---

## 4. 使用方式（与原来相同）

```bash
export REI_ROBOT=fox_three

ros2 launch fox_slam_ros2 cartographer.launch.py   # 建图（已包含底盘/雷达/机器人模型/RViz）
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 保存地图
ros2 launch fox_slam_ros2 map_saver.launch.py \
  map_file:=test_map \
  map_directory:=/home/ubuntu/ros2fox/maps
```

---

## 5. 踩坑记录（重要）

| # | 现象 | 原因 | 解决 |
|---|------|------|------|
| 1 | `Topmost item on Lua stack is not a table!` | lua 配置末尾缺少 `return options` | 文件末尾必须加 `return options` |
| 2 | `Key 'max_distance_m' was used the wrong number of times` | `motion_filter` 参数名写错 | 用 `max_distance_meters` / `max_angle_radians`（不是 `_m`/`_rad`） |
| 3 | `Key 'resolution' was used the wrong number of times` | Humble 中 submap 分辨率路径改变 | 用 `TRAJECTORY_BUILDER_2D.submaps.grid_options_2d.resolution` |
| 4 | `TypeError: unsupported operand type(s) for +`（map_saver） | `LaunchConfiguration` 不能 `+` 字符串 | 用 `launch.substitutions.PathJoinSubstitution` 组合路径 |
| 5 | `ImportError: cannot import name 'PathJoinSubstitution'` | Humble 中导入路径不同 | 从 `launch.substitutions` 导入（`launch_ros.substitutions` 是 Iron+ 才有） |

> 通用规则：Cartographer 会检查配置中每个键是否被代码读取，**参数名拼错会导致启动即崩溃**。
> 覆盖参数前，先对照官方模板确认参数名：
> - `/opt/ros/humble/share/cartographer/configuration_files/trajectory_builder_2d.lua`
> - `/opt/ros/humble/share/cartographer/configuration_files/pose_graph.lua`

---

## 6. 如何切回 SLAM Toolbox

只需把启动命令改回旧 launch：

```bash
ros2 launch fox_slam_ros2 fox_slam.launch.py
```

并同步更新 `启动` 脚本中的建图命令即可。两个方案互不影响。

---

## 7. 相关文件清单

```
src/fox_slam_ros2/
├── config/
│   ├── cartographer_fox.lua     # ★ 新增：Cartographer 配置
│   ├── fox_slam_params.yaml     # SLAM Toolbox 配置（保留备用）
│   └── fox_lidar_params.yaml    # ydlidar 配置
├── launch/
│   ├── cartographer.launch.py   # ★ 新增：Cartographer 建图 launch
│   ├── fox_slam.launch.py       # SLAM Toolbox 建图 launch（保留备用）
│   ├── fox_lidar.launch.py
│   └── map_saver.launch.py      # 存图 launch（已修复路径拼接）
├── package.xml                  # 已添加 cartographer_ros 依赖
└── CARTOGRAPHER_SWITCH.md       # ★ 本文档
```
