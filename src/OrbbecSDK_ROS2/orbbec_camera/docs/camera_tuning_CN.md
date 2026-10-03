# Astra Pro 相机调参指南

> 本文档针对 `/home/ubuntu/ros2fox` 上 Astra Pro (PID 0x0403) 相机，
> 解决「分辨率低」「远处葡萄深度识别不到」两类问题。

## 一、已发现的问题（代码层面）

1. **对齐深度话题缺失**：`astra_pro_plus.launch.py` 默认 `depth_registration=false`，
   导致 `/camera/aligned_depth_to_color/image_raw` **根本不会发布**。
   而葡萄采摘节点 (`harvest_node.py`) 与检测测试 (`test_detection.py`) 都订阅这个话题，
   所以深度定位实际从未生效（不是单纯的"被过滤"）。
   → **已修复**：launch 默认改为 `depth_registration:=true`。

2. **软滤波 (soft filter) 可能滤掉远处稀疏点**：
   `enable_soft_filter=true` 时设备默认的斑点尺寸阈值会把"孤立/稀疏"的深度点判为噪声清除。
   远处葡萄反光弱、深度噪声大、点稀疏，最容易被滤掉。
   → 用下方 `camera_tuner` 实测，可关闭软滤波或调大 `speckle_size`。

3. **LDP / 激光能量**：`enable_ldp=true`、`laser_energy_level=-1`(默认)。
   远处目标可适当提高激光能量 (`laser_energy`) 提升信噪比。

## 二、分辨率说明

- 当前设备 Astra Pro (0x0403)，RGB / 深度 / IR 常规上限为 **640x480@30fps**。
- 运行下方工具可枚举设备**实际支持的全部分辨率与深度工作模式**：
  ```
  camera_tuner --list
  ```
- 若确实需要更高分辨率（如 1280x960），需要更换支持更高分辨率的设备
  （例如 Astra Pro Plus / 0x0501）。工具会如实打印设备型号与 PID。

### 实际枚举结果（本机 Astra Pro，固件 RD2403，USB2.0）

| 流 | 支持的分辨率 |
|----|--------------|
| Color | **1280x720 @30fps (RGB/MJPG)**、1280x800@30fps、640x480@30fps、… |
| Depth | **640x480 @30fps (Y11/Y12)**（30fps 下最高）、1280x1024@7fps、320x240、160x120 |
| IR    | 640x480@30fps、1280x1024@7fps、1280x960@7fps、1280x720@7fps |

- **彩色可提升到 1280x720@30fps**（YOLO 检测更清晰）。注意 USB2.0 带宽有限，
  若节点同时开 彩色+深度+IR 三流，1280x720 RGB 可能带宽不足，建议用 MJPG 格式并实测。
- **深度 640x480@30fps 已是 30fps 上限**；1280x1024 只有 7fps，不适合动态抓取。
- 该设备**不支持** LDP / 激光能量 / 激光开关（`enable_ldp`、`laser_energy_level` 参数无效）。
- 设备默认软滤波参数：`soft_filter=ON`、`max_diff=16`、`speckle_size=480`。
  实测关闭软滤波后有效深度像素由 82.7% 提升到 85.1%（远处场景差异更明显）。

## 三、调参工具 camera_tuner

编译（首次新增工具后需要重新 build）：
```bash
cd ~/ros2fox
colcon build --packages-select orbbec_camera
source install/setup.bash
```

**使用前必须先停止正在运行的相机节点**（设备需独占访问）：
```bash
# 停相机（在你启动相机的终端按 Ctrl+C，或：）
pkill -f "component_container" || true
```

### 1) 枚举设备能力 + 当前参数 + 导出 YAML
```bash
camera_tuner --list --out /tmp/camera_settings.yaml
```
会打印：设备型号/PID、全部支持的分辨率、深度工作模式、关键属性当前值。

### 2) 关闭软滤波 + LDP、提高激光能量，并捕获对比帧
```bash
camera_tuner --set soft_filter=off --set ldp=off --set laser_energy=8 \
             --capture /tmp/tune_a
```
生成：
- `depth_colored.png` 伪彩色深度（**重点看远处葡萄是否有有效深度**）
- `depth_raw.pgm` 原始 16bit 深度
- `ir.png`、`color.png`

### 3) 保留软滤波但放宽斑点阈值，捕获对比
```bash
camera_tuner --set soft_filter=on --set speckle_size=2000 --set max_diff=20 \
             --capture /tmp/tune_b
```

### 4) 切换深度工作模式后再捕获
```bash
camera_tuner --depth-mode "High Accuracy" --capture /tmp/tune_c
```

> 用不同组合多跑几次，对比 `depth_colored.png` 里远处葡萄区域的深度有效性与噪声，
> 选出效果最好的参数组合。

## 四、把合适参数更新到 launch

编辑 `/home/ubuntu/ros2fox/src/OrbbecSDK_ROS2/orbbec_camera/launch/astra_pro_plus.launch.py`，
把对应 `DeclareLaunchArgument` 的 `default_value` 改为你实测的合适值，例如：

```python
DeclareLaunchArgument('enable_soft_filter', default_value='false'),
DeclareLaunchArgument('soft_filter_max_diff', default_value='-1'),
DeclareLaunchArgument('soft_filter_speckle_size', default_value='-1'),
DeclareLaunchArgument('enable_ldp', default_value='false'),
DeclareLaunchArgument('laser_energy_level', default_value='8'),
```

也可以不改默认值，启动时临时覆盖：
```bash
ros2 launch orbbec_camera astra_pro_plus.launch.py \
  enable_soft_filter:=false enable_ldp:=false laser_energy_level:=8 \
  color_info_url:=file:///home/ubuntu/ros2fox/calib_result/camera_calib.yaml
```

## 五、验证深度识别

重启相机（`depth_registration:=true` 已默认）后：
```bash
# 确认对齐深度话题存在
ros2 topic list | grep aligned_depth
# 运行检测测试
ros2 run fox_grape_harvest test_detection.py
```
远处葡萄应能显示深度值并在图上标注 3D 坐标。
