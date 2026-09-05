# 🤖 众灵总线舵机夹爪 ROS2 控制包

> 包名: `gripper_control`  
> 适用: 众灵科技 ZL-Robot 总线舵机 (单线半双工, 115200bps)  
> 协议: ASCII 文本 `#IDP脉宽T时间!`  
> 舵机 ID: 1 (默认)

---

## � ROS2 使用

### 1. 编译

```bash
cd ~/havest_robot
conda deactivate
source /opt/ros/humble/setup.bash
colcon build --packages-select gripper_control
source install/setup.bash
```

### 2. 启动节点

```bash
ros2 run gripper_control gripper_node.py
```

> 节点会自动检测串口（udev 绑定 `/dev/ttyGripper`）和配置波特率。

### 3. 控制夹爪

```bash
# 抓取（抓紧/闭合）脉宽 2000
ros2 service call /gripper/grip std_srvs/srv/SetBool "{data: true}"

# 松开（张开）脉宽 500
ros2 service call /gripper/grip std_srvs/srv/SetBool "{data: false}"
```

服务返回 `success=true` 表示指令已发送。

### 4. 集成到机械臂

```bash
ros2 launch gripper_control gripper_with_arm.launch.py
```

| 集成服务 | 说明 |
|---------|------|
| `/integrated_pick` | 预抓取→下降→夹紧→抬升 |
| `/integrated_place` | 预放置→下降→松开→抬升 |
| `/integrated_grip` | 仅控制夹爪 |

示例：
```bash
ros2 service call /integrated_pick arm_controller/srv/Move \
  "{pose: {position: {x: 200, y: 0, z: 100}, roll: 0.0}}"
```

---

## 🔌 硬件接线

众灵总线舵机是**单线半双工**通信，CH340 的 TX 和 RX 必须**短接**后接舵机信号线：

```
众灵舵机               CH340 USB-TTL
───────                ─────────────
信号线(橙/白) ────┬─── TXD
                  └─── RXD    ← TX 和 RX 短接在一起！
正极(红色)   ──────── 外接电源 5~8.4V 正极
负极(棕/黑)  ──────── CH340 GND + 电源 GND (共地)
```

> ⚠️ **关键**：CH340 的 TXD 和 RXD 必须用杜邦线或焊锡**短接**，否则舵机无法通信。  
> ⚠️ 舵机需要**外接电源**（5~8.4V），USB 供电不足。

> 🔥🔥 **最重要的防烧板警告（2026-08-09 教训）**：
> 舵机用独立电源时，**独立电源的负极必须和 CH340 的 GND 接到一起（共地）**！
> 如果不共地，舵机信号线（接在 CH340 短接的 TX/RX 上）会相对 CH340 悬空，
> 容易把舵机的电压反灌进 CH340 芯片 → **烧毁转接板**。
> 烧板典型症状：`lsusb` 看不到 CH340、dmesg 报
> `device descriptor read/64, error -110` / `unable to enumerate USB device`。
> 出现这种症状 = 板子已坏，换板即可；换板后先单独插 USB 测试，再接舵机。

---

## 📁 包结构

```
src/gripper_control/
├── package.xml
├── CMakeLists.txt
├── scripts/
│   ├── gripper_node.py          # 夹爪控制节点（核心）
│   └── gripper_integration.py   # 夹爪+机械臂集成节点
├── launch/
│   ├── gripper.launch.py        # 仅启动夹爪
│   └── gripper_with_arm.launch.py  # 夹爪+集成一键启动
└── 说明.md                      # 本文档
```

---

## ⚙️ 参数说明

可在命令行覆盖：

```bash
ros2 run gripper_control gripper_node.py --ros-args \
  -p port:=/dev/ttyGripper \
  -p servo_id:=1 \
  -p pulse_min:=500 \
  -p pulse_max:=2000 \
  -p move_time_ms:=1500
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `port` | `/dev/ttyGripper` | 串口设备路径 (udev 绑定 CH340) |
| `baudrate` | 115200 | 波特率 |
| `servo_id` | 1 | 舵机 ID (众灵默认 0，实际设为 1) |
| `pulse_min` | 500 | 松开脉宽 (对应张开) |
| `pulse_max` | 2000 | 抓紧脉宽 (对应闭合) |
| `pulse_mid` | 1250 | 中位脉宽 |
| `move_time_ms` | 1500 | 动作时间 (毫秒) |

> 💡 **调参技巧**：如果夹不紧，增大 `pulse_max`（如 2200）；如果松不开，减小 `pulse_min`（如 400）。先用 `echo` 命令找到合适值再写入参数。

---

## 🧪 手动测试

如果节点有问题，先用命令行直接测试舵机：

```bash
# 配置串口
sudo stty -F /dev/ttyGripper 115200 cs8 -cstopb -parenb raw -echo

# 中位
echo -en '#001P1250T1000!\n' > /dev/ttyGripper

# 抓紧(闭合)
echo -en '#001P2000T1000!\n' > /dev/ttyGripper

# 松开(张开)
echo -en '#001P0500T1000!\n' > /dev/ttyGripper
```

> ⚠️ 注意脉宽格式：**必须补零到 4 位**，如 `P0500` 而不是 `P500`。

---

## ⚠️ 常见问题

### Q: 服务返回成功但舵机不动？
- 检查 TX/RX 是否短接
- 检查 `servo_id` 参数是否正确（用 `echo -en '#001PID!\n'` 检测）
- 脉宽格式必须是 4 位（`P0500` 不是 `P500`）

### Q: 之前能控制，突然不动了？
拔插 USB 转串口模块重置硬件，然后重新启动节点。

### Q: 夹不紧或张不开？
调整 `pulse_min` 和 `pulse_max` 参数。用 `echo` 命令逐个值测试找到合适的范围。

### Q: Python 版本冲突？
ROS2 Humble 需要 Python 3.10，运行前先 `conda deactivate` 退出 conda 环境，然后重新 source ROS2 环境。

---

## 📋 协议参考

众灵总线舵机 ASCII 指令格式：

| 指令 | 说明 |
|------|------|
| `#001P2000T1000!` | ID=1 转到脉宽 2000(抓紧/闭合)，时间 1000ms |
| `#001P0500T1000!` | ID=1 转到脉宽 500(松开/张开)，时间 1000ms |
| `#001PRAD!` | 读取当前角度 |
| `#001PID!` | 检测舵机是否存在 |
| `#001PID002!` | 修改舵机 ID 为 002 |
| `{G0000#001P...!#002P...!}` | 多舵机同步指令 |

脉宽范围：500(松开) ~ 1250(中位) ~ 2000(抓紧)
