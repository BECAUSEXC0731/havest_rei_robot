# FOX 葡萄采摘机器人 WebUI — 项目构建任务清单

> 版本：v1.1（2026-09-30）
> 关联文档：[WebUI 技术文档](WebUI_技术文档.md)、[AGENTS.md](../AGENTS.md)
> **v1.1 变更**：S4 多机定稿为 **方案 C（对称 HTTP 聚合）** —— 每台机都跑 Agent，各机之间用 HTTP
> 互拉 `/api/state`，因此**任意一台的 `:8080` 都能看到全部机器**（技术文档 §3.2 / §7.4）。
> 原"模式 A（多 domain）/模式 B（Zenoh）"降级为可选形态（见 S4-附）。
> 目标：把 WebUI 从零构建到可用，**每个任务都必须有可执行的验证命令与明确的通过标准**，并在阶段末尾的"验证记录表"里填写实测结果。

---

## 0. 使用说明与全局约定

### 0.1 任务编号规则

| 前缀 | 含义 |
|---|---|
| `S0` | 前置准备（环境、依赖、基线快照） |
| `S1` | 只读状态可视化（能看） |
| `S2` | 视频与前端框架（看得清） |
| `S3` | 控制与模块启停（能动、能干活） |
| `S4` | 多机聚合（一屏看多台） |
| `S5` | Zenoh / FastAPI / Three.js（跨网与增强） |
| `S6` | 打磨与验收（好用） |

### 0.2 每个任务的标准格式

```
### T<阶段>.<序号> 任务名
- 做：要写的文件 / 关键实现点
- 命令：复现该任务的命令（可直接复制执行）
- 验证：验证命令 + 【通过标准】
- 不通过时：排查方向
```

### 0.3 ⚠️ 本项目必须遵守的工程约定（踩过坑）

1. **改 `src` 下任何 Python 脚本/launch/param 后，必须 `colcon build --packages-select <包名>`**，否则 `ros2 run/launch` 用的还是 `install/` 里的旧副本。
2. **终端环境用 zsh**：`source /opt/ros/humble/setup.zsh && source ~/ros2fox/install/setup.zsh`（`setup.bash` 在 zsh 下会报 `BASH_SOURCE` 错误）。
3. **深度话题 `/camera/depth/image_raw` 是 `16UC1`，单位是厘米（cm）**，转米是 `/100`，**不是 `/1000`**。任何深度换算改动都要用尺子回归一次。
4. **相机必须带正确内参启动**：`color_info_url:=file:///home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml`（fx≈607）。内参错 → 手眼与像素→3D 全错。
5. **导航参数改动要同步 `install`**：`diff src/fox_navigation_ros2/param/nav2_params.yaml install/fox_navigation_ros2/share/fox_navigation_ros2/param/nav2_params.yaml` 必须为空。
6. **启动雷达前清理残留进程**，否则报 `Unknown error`（端口被占用）：`pkill -f ydlidar`。
7. WebUI 只能启动**白名单**命令，**严禁**把前端传来的字符串直接拼进 shell（RCE 风险）。

### 0.4 阶段验收原则

- 每个任务：单点验证通过即可勾选。
- 每个阶段末尾：必须跑完该阶段的**端到端验收**（模拟真实使用路径），并在记录表里写「实测结果 + 结论」。

---

## S0. 前置准备

### T0.1 确认 ROS2 工作区基线可用

- 做：确认能构建现有包、能列出关键接口。
- 命令：
  ```bash
  source /opt/ros/humble/setup.zsh && source ~/ros2fox/install/setup.zsh
  ros2 pkg list | grep -E "arm_controller|fox_grape_harvest|gripper_control|rei_robot_base|fox_navigation_ros2"
  ```
- 验证：6 个包名全部出现。【通过标准】无 `Package not found` 报错。
- 不通过时：先 `cd ~/ros2fox && colcon build --packages-select <缺的包>`。

### T0.2 安装/确认 Python 依赖

- 做：确认已有 `flask / aiohttp / cv2 / numpy / PIL / ultralytics / torch`；安装 `fastapi` 与 `uvicorn`（S5 用，先装好）。
- 命令：
  ```bash
  python3 -c "import flask, aiohttp, cv2, numpy, PIL, ultralytics; print('base deps OK')"
  pip3 install fastapi uvicorn
  python3 -c "import fastapi, uvicorn; print(fastapi.__version__, uvicorn.__version__)"
  ```
- 验证：两条命令都打印版本/OK。【通过标准】无 `ModuleNotFoundError`。
- 不通过时：检查外网（此前实测 pypi 可达）；离线则改用已装的 `flask`（后端代码需保持"框架可切换"）。

### T0.3 下载并本地化前端库（免构建方案的关键）

- 做：把 3 个文件放到 `src/fox_webui/web/lib/`：`vue.esm-browser.prod.js`、`three.module.js`、`OrbitControls.js`。
- 命令：
  ```bash
  mkdir -p ~/ros2fox/src/fox_webui/web/lib
  ls -l ~/ros2fox/src/fox_webui/web/lib/
  ```
- 验证：3 个文件存在且每个 > 80KB（Three.js 通常 > 600KB）。【通过标准】文件齐全、大小合理，后续页面无 404。
- 不通过时：确认网络；**不要**改成 CDN 引用（现场机器人可能无外网）。

### T0.4 保存系统接口基线快照（后续所有验证的对照物）

- 做：把当前运行系统的接口快照存档。
- 命令：
  ```bash
  mkdir -p ~/ros2fox/docs/baseline
  ros2 topic list   > ~/ros2fox/docs/baseline/topics.txt
  ros2 service list > ~/ros2fox/docs/baseline/services.txt
  ros2 action list  > ~/ros2fox/docs/baseline/actions.txt
  grep -c . ~/ros2fox/docs/baseline/*.txt
  ```
- 验证：三个文件非空，且 `topics.txt` 含 `/odom /cmd_vel /camera/color/image_raw`；`services.txt` 含 `/goto_position /gripper/grip /home`；`actions.txt` 含 `/navigate_to_pose`。【通过标准】关键接口齐全。
- 不通过时：说明对应节点没启动，先按 `启动.txt` 把该节点起来再快照。

### T0.5 生成基线状态快照（数值对照）

- 做：记录手眼标定与内参的实际值，作为 WebUI 显示正确性的对照。
- 命令：
  ```bash
  # 彩色内参（CameraInfo YAML 是 camera_matrix.data 数组格式，不是 fx:/fy: 键！）
  sed -n '1,15p' /home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml
  python3 -c "import json;d=json.load(open('/home/ubuntu/ros2fox/calib_result/hand_eye_result.json'));print({k:v for k,v in d.items() if k in ('avg_error','max_error','t','rms')})"
  ```
- 验证：`camera_matrix.data` 第 1 项 fx≈607.47、第 5 项 fy≈603.83、第 3 项 cx≈323.42、第 6 项 cy≈245.52；手眼误差可打印。【通过标准】数值与 AGENTS.md/记忆记录一致。
- 不通过时：标定文件被覆盖，需重做标定（不在本任务范围，先记录差异）。

**阶段记录表（2026-09-17 实测）**

| 任务 | 验证命令 | 期望结果 | 实测结果 | 结论 |
|---|---|---|---|---|
| T0.1 | `ros2 pkg list \| grep ...` | 6 个包 | 6 个包全部列出（362 个包中共命中 6 个） | ✅ 通过 |
| T0.2 | `python3 -c "import fastapi"` | 打印版本 | fastapi 0.141.1 / uvicorn 0.53.0 | ✅ 通过 |
| T0.3 | `ls -l web/lib/` | 3 个 js | vue 150KB(v3.4.38) / three 872KB / OrbitControls 30KB | ✅ 通过 |
| T0.4 | `ls docs/baseline/` | 3 个文件含关键接口 | **延后**：机器人系统未启动，等到 S3 有真实节点时再抓 | ⏸ 延后 |
| T0.5 | 内参/手眼数值 | fx≈607 | fx=607.4669 fy=603.8284 cx=323.4215 cy=245.5242 | ✅ 通过（并修正了文档里的错误命令，见下） |
| **T0.6（新增）** | `source scripts/fox_webui_env.sh && python3 -c "import arm_controller, rei_robot_base, fox_webui"` | 三者可导入 | `imports OK` | ✅ 通过（见下方"环境三坑"） |

> **T0.5 修正**：`color_camera_info.yaml` 是 **CameraInfo 格式（`camera_matrix.data` 数组）**，
> 不是 `fx:`/`fy:` 键值对，原命令 `grep -E "fx|fy|cx|cy"` 匹配不到任何东西（实测确认）。
> 正确做法见 T0.5 已更新的命令。

---

## S1. 只读状态可视化（"能看"）

> 目标：在浏览器里看到 **机械臂 XYZ、电池电压、地图坐标、夹爪开合、底盘线/角速度、模块健康、日志**。

### T1.1 创建 `fox_webui` 包骨架

- 做：`src/fox_webui/{package.xml, setup.py, setup.cfg, resource/fox_webui, fox_webui/__init__.py, web/}`；`entry_points` 先注册 `fox_webui_agent`。
- 命令：
  ```bash
  cd ~/ros2fox && colcon build --packages-select fox_webui
  source install/setup.zsh && ros2 pkg prefix fox_webui
  ```
- 验证：构建成功且打印路径。【通过标准】`ros2 run fox_webui fox_webui_agent` 不报 `No executable found`（对照项目已知坑：脚本必须进 `console_scripts`）。
- 不通过时：检查 `setup.py` 的 `console_scripts` 键名与安装 `lib/` 目录。

### T1.2 `state.py` — 状态采集器

- 做：订阅/采集下列数据，统一写入带锁的共享快照（10Hz）：
  | 字段 | 来源 |
  |---|---|
  | `arm_xyz` | `/arm_controller/position_info`（`arm_controller/Control`：`position` + `roll/pitch/yaw`） |
  | `battery_v` / `charging` | `/car_data`（`CarData.power_voltage` / `is_charge`） |
  | `motor_speed[]` `crash[]` `smoke` | `/car_data` |
  | `odom_pose` / `vel(vx,vy,vth)` | `/odom`（`nav_msgs/Odometry`） |
  | `cmd_vel` | `/cmd_vel` |
  | `map_pose(x,y,yaw)` | TF `map→base_footprint`（`tf2_ros.Buffer.lookup_transform`）+ 兜底 `/lidar_loc_pose` |
  | `gripper` | `/gripper/state`（T1.3 新增） |
  | `health` | 每个话题的"最后收到时间 + 估算频率" |
- 命令：
  ```bash
  ros2 run fox_webui fox_webui_agent --ros-args -p port:=8080
  # 另开终端：
  curl -s localhost:8080/api/state | python3 -m json.tool | head -40
  ```
- 验证：JSON 里 `battery_v`、`odom_vel`、`arm_xyz`、`map_pose` 都有值。【通过标准】与 `ros2 topic echo /car_data --once` 的电压偏差 < 0.05V；`map_pose` 与 RViz 中机器人位置量级一致。
- 不通过时：`ros2 topic hz <话题>` 确认数据源在发；检查 QoS（图像/雷达用 `qos_profile_sensor_data`）。

### T1.3 给 `gripper_node.py` 增加状态发布（必做的小改）

- 做：新增发布 `/gripper/state`（`std_msgs/Int32` 脉宽，或自定义含开度%+时间戳的消息），在 `grip_callback` 后发布；可选用 `#IDPRAD!` 回读角度。
- 命令：
  ```bash
  cd ~/ros2fox && colcon build --packages-select gripper_control
  ros2 run gripper_control gripper_node.py
  ros2 topic echo /gripper/state --once
  ros2 service call /gripper/grip std_srvs/srv/SetBool "{data: true}"
  ros2 topic echo /gripper/state --once
  ```
- 验证：两次 echo 分别出现 `500`（松开）与 `2000`（抓紧）。【通过标准】脉宽值与项目实测定义一致（**2000=抓紧、500=松开**）。
- 不通过时：确认 `install/gripper_control/lib/gripper_control/gripper_node.py` 已更新（未重编则跑的是旧副本）。

### T1.4 Web 服务骨架 + 状态 API + SSE 推送

- 做：`webapi.py` 暴露：
  `GET /api/state`（快照）、`GET /api/health`（话题心跳）、`GET /api/stream`（SSE，10Hz）、静态托管 `web/`。
- 命令：
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/api/state
  curl -s localhost:8080/api/health | python3 -m json.tool
  timeout 3 curl -sN localhost:8080/api/stream | grep -c "^data:" || true
  ```
- 验证：HTTP 200；SSE 3 秒内 `data:` 行 ≥ 20（10Hz）。【通过标准】页面首次加载时间 < 1s，SSE 不中断。
- 不通过时：SSE 需关闭代理缓冲；确认 rclpy 线程与 asyncio 线程通过"快照"解耦（见技术文档 §5）。

### T1.5 首版只读页面（原生 HTML + 表格，先不引框架）

- 做：`web/index.html` + `app.js`：连 SSE，把状态渲染为卡片/表格（机械臂、电池、底盘、夹爪、定位、健康）。
- 命令：浏览器打开 `http://<Jetson-IP>:8080`。
- 验证：数值每秒变化多次；**电池电压与 `ros2 topic echo /car_data` 数值一致**；拔掉夹爪线或停掉节点后对应卡片变灰/红。【通过标准】数值实时且无 NaN/undefined。
- 不通过时：看浏览器 Console 与后端日志。

### T1.6 话题健康与"节点是否在跑"面板

- 做：把 `state.health` 渲染成列表（在线/掉线 + 频率），掉线 3s 判定。
- 命令：
  ```bash
  pkill -f ydlidar_ros2_driver   # 人为制造掉线
  ```
- 验证：3 秒内 `/scan` 变为"掉线"。【通过标准】掉线判定延迟 ≤ 3s，恢复后自动转回绿色。
- 不通过时：心跳窗口调大/调小（阈值参数化）。

### T1.7 日志面板（`/rosout`）

- 做：订阅 `/rosout`（`rcl_interfaces/msg/Log`），按级别过滤 + 环形缓冲（默认 500 条）+ 自动滚屏。
- 命令：制造一条警告（如启动相机前先看日志）。
- 验证：面板出现 INFO/WARN 文本且能按级别过滤。【通过标准】200 条/秒的日志下页面不卡。
- 不通过时：前端做批量渲染（每 200ms 合并一次 DOM 更新）。

**阶段验收（S1 端到端）**
1. 只启动底盘+雷达+机械臂+夹爪（不启相机/采摘），页面应显示：坐标、速度、电压、机械臂 XYZ、夹爪状态、健康列表。
2. 手动搬动机械臂末端（或 `ros2 service call /goto_position ...`），页面 XYZ 跟随变化。
3. 停掉底盘 → 3s 内 `/odom` 掉线、速度显示归零/变灰。

**阶段记录表（2026-09-17 实测：用 `scripts/fake_telemetry.py` 灌假数据验证，无需硬件）**

| 任务 | 验证命令 | 期望结果 | 实测结果 | 结论 |
|---|---|---|---|---|
| T1.1 | `colcon build --packages-select fox_webui gripper_control` | 构建成功 | 2 packages finished [1min 23s]；`install/fox_webui/lib/fox_webui/fox_webui_agent` 可执行；`share/fox_webui/web/lib/` 子目录结构正确保留 | ✅ 通过 |
| T1.2 | `curl /api/state` 对比注入值 | 字段齐全、数值一致 | twist={vx:0.15,vy:0.02,vth:0.3}、battery={24.5V,charging:true}、arm={200.0, 11.849(=10+3sin), 130.0}、chassis.motor_speed=[12.0,11.5,12.2]、pose={1.0,2.0,src:lidar_loc} —— **与注入值完全一致** | ✅ 通过 |
| T1.3 | `echo /gripper/state` → 快照 ratio | 2000→闭合、500→开 | pulse=2000 → ratio=0.0 / closed=True（换算正确）；源码与 install 副本均已含发布（`grep -c` = 2） | ✅ 通过（硬件动作待 S3 实测） |
| T1.4 | `curl /api/stream` | ≥20 条 data/3s | 25 条 / 3s（≈8.3Hz） | ✅ 通过 |
| T1.5 | 浏览器打开页面 | 数值实时 | 截图确认：🍇 标题、🟢机器人在线、定位 1.000/2.000、vx 0.15、电池 24.50 全部上屏且实时刷新 | ✅ 通过 |
| T1.6 | 话题健康表 | 在线/掉线判定正确 | 有数据的 7 个话题 online=True 且频率精确（/odom 10.0Hz、/car_data 5.0Hz、机械臂 10.0Hz、夹爪 2.0Hz、/cmd_vel 1.0Hz、/lidar_loc_pose 10.0Hz）；未启动的 /scan /map /plan /camera_info 正确显示"无数据" | ✅ 通过 |
| T1.7 | 日志面板 | INFO 可见、可过滤 | `/api/logs` 返回 `20 fake_telemetry | fake_telemetry: 心跳…`，页面按 22:11:19…22:12:26 时间序列滚动显示，级别过滤/自动滚屏/清空按钮正常 | ✅ 通过 |
| **T1.8（新增）** | 按话题超时修正 | /rosout 不误报掉线 | 修正前：/rosout 显示"掉线"（5s 一条心跳 vs 3s 统一超时）→ 修正后：`online=True age=2.0 timeout=20.0` | ✅ 通过（真 bug，已修） |

---

## S2. 视频与前端框架（"看得清"）

### T2.1 `video.py` — MJPEG 三源（彩色 / 深度伪彩 / 识别叠加）

- 做：`GET /video/{color|depth|detect}` 返回 `multipart/x-mixed-replace`；`cv2.imencode('.jpg', frame, [IMWRITE_JPEG_QUALITY, 70])`，彩色 640×480@10fps。
- 命令：
  ```bash
  curl -sI localhost:8080/video/color | head -3
  curl -s --max-time 2 localhost:8080/video/color | wc -c
  ```
- 验证：`Content-Type: multipart/x-mixed-replace; boundary=frame`；2 秒内字节数 > 20KB。【通过标准】浏览器 `<img src="/video/color">` 出图且延迟 < 500ms。
- 不通过时：确认相机已启动、话题有数据（`ros2 topic hz /camera/color/image_raw`）、`cv_bridge` 编码正确（RGB→BGR）。

### T2.2 按需订阅（无观看者时零开销）

- 做：视频"代理"做引用计数：第 1 个观看者到来才订阅+编码，最后一个离开即退订。
- 命令：
  ```bash
  top -bn1 | grep fox_webui          # 无观看者
  # 浏览器打开视频后再执行一次
  ```
- 验证：无观看者时进程 CPU **< 5%**；观看时 CPU 上升但 < 60%（Orin Nano）。【通过标准】不打开视频绝不拖累导航。
- 不通过时：检查是否误写成"启动即订阅"。

### T2.3 深度伪彩（回归项目已知坑）

- 做：`16UC1` **厘米** → `float32 米 = v/100`；截断到 0.2~2.5m 归一化后上色（colormap），画面角上叠加当前中心点距离（米）。
- 命令：把平板/葡萄放到尺子量好的 **50 cm** 处。
- 验证：界面读数 ≈ 0.50 m（允许 ±3 cm）。【通过标准】**不出现 /1000 造成的"最远只有 40cm"现象**。
- 不通过时：检查是否 `/1000` 或把 `32FC1` 也除了 100。

### T2.4 前端切换到 Vue3（ESM 免构建）+ 组件化

- 做：`index.html` 用 `importmap` 指向 `web/lib/vue.esm-browser.prod.js`；组件：`MapView / VideoPanel / RobotStatus / ArmPanel / GripperPanel / NavPanel / ModulePanel / LogPanel`（先只做 Status/Log）。
- 命令：浏览器 Console 检查。
- 验证：无 `404`、无 `Failed to resolve module specifier`；状态仍 10Hz 更新。【通过标准】页面无报错、无闪烁。
- 不通过时：`importmap` 路径以 `/lib/...` 开头（需后端把 `web/` 作为静态根）。

### T2.5 2D Canvas 地图（底图 + 位姿 + 激光 + 全局路径 + 目标点）

- 做：后端 `GET /api/map`（解析 `maps/*.yaml`+PGM → 分辨率/origin/栅格数组）；前端 Canvas 绘制：
  - 世界→像素：`px=(x-ox)/res`，`py=H-(y-oy)/res`（ROS 栅格约定：`0`=障碍、`254`=自由、`205`=未知，受 YAML 的 `negate`/`occupied_thresh` 影响，务必按 YAML 解析）
  - 叠加：`/scan` 激光点、`/plan` 全局路径、机器人箭头（yaw）
- 命令：与 RViz 同屏对比。
- 验证：机器人在 Canvas 上的位置与 RViz **误差 < 5 cm、朝向 < 2°**；激光点与地图墙体对齐。【通过标准】能凭地图判断"车在哪"。
- 不通过时：核对 `origin`/`resolution` 与 y 轴翻转公式；确认取的是 `map→base_footprint`（不是 `base_link`）。

### T2.6 实时识别（`preview_detector`）

- 做：新增 3Hz 检测线程：订阅彩色+深度+`camera_info`，复用 `fox_grape_harvest` 的 `YoloDetector`、`depth_utils`（**不重写**，避免与主流程双实现漂移）；发布 `/fox_webui/preview_image` 与 `/fox_webui/detections`（含框、像素坐标、机器人系 mm 坐标、可抓性等级 `GRASP/MARGINAL/UNREACHABLE`）。
- 命令：
  ```bash
  ros2 topic hz /fox_webui/preview_image
  ros2 topic echo /fox_webui/detections --once
  ```
- 验证：预览 3Hz 左右；把葡萄放进视野 → 检测列表出现条目，坐标与 `ros2 run fox_grape_harvest test_detection.py` 输出**同量级（±2 cm）**。【通过标准】可抓性等级与主流程判定一致。
- 不通过时：确认 `models/grape.pt` 存在、内参正确、`color_ir_extrinsic.json` 被加载（手动 D2C）。

**阶段验收（S2 端到端）**
1. 启动导航+相机+WebUI，页面显示地图、机器人位置、激光、视频。
2. 切到"识别"源，视野内葡萄被框出并给出机器人系坐标。
3. 关闭视频卡片 → CPU 明显回落（验证按需订阅有效）。

**阶段记录表（2026-09-19 实测：用 `fake_telemetry.py --all` 提供合成相机/激光/路径，无需硬件）**

| 任务 | 验证命令 | 期望结果 | 实测结果 | 结论 |
|---|---|---|---|---|
| T2.1 | `curl -sI /video/color` + 计数帧 | multipart + 有帧 | color/depth/detect 三源均出流（2s 内分别 38KB/6 帧、48KB、61KB/6 帧） | ✅ 通过 |
| T2.2 | `/api/health` 看 `video_viewers` | 无观看者时全 0 | 流前 0/0/0 → 流中 color=2 → 流结束后自动回 0/0/0 | ✅ 通过（按需订阅生效） |
| T2.3 | 50cm → 是否 0.50m | 0.50 m | `render_depth` 单元回归输出 `center=0.50m range=0.2-2.5m`；假数据 60cm → 识别结果 `depth_m=0.611` | ✅ 通过（“/100 而非 /1000”锁定） |
| T2.4 | 浏览器 Console + 页面 | 无 404/报错、组件正常 | Vue3 ESM 免构建加载正常；截图确认地图/视频/状态/健康/日志五区均渲染 | ✅ 通过 |
| T2.5 | 地图 canvas vs 期望 | 位置/朝向正确 | canvas 435×300；截图可见真实地图轮廓 + 蓝色机器人箭头(1,2) + 红色激光环 + 绿色路径 | ✅ 通过 |
| T2.6 | `/api/detections` | 有坐标且可抓 | `depth_m=0.611`、`robot_mm=[231.9,178.3,95.8]`、`reach=GRASP`（走完 D2C→手眼→可抓性全链路） | ✅ 通过（sim 模式；真实模型需模型可用） |
| **T2.7（新增，真 bug）** | 反复开关视频流后 `/api/ping` | 仍即时响应 | 修复前：开/关几轮后**整个后端卡死**（CPU 70.8%，36 线程）→ 根因=同步生成器占死线程池；改 asyncio 异步生成器 + 非阻塞取帧后：3 轮开关后 ping 正常，线程 26，CPU 19.8% | ✅ 通过 |
| **T2.8（新增，真 bug）** | 图像回调是否丢帧降频 | 不每帧转换 | 加上 `min_interval` 丢帧后 CPU 70.8%→28.5%（三路流并发） | ✅ 通过 |
| **T2.9（新增，真 bug）** | `camera_info` 能收到吗 | `has_K=True` | 识别器原用 RELIABLE 订阅而相机是 BEST_EFFORT → 永远收不到内参；改用 `qos_profile_sensor_data` 后 `has_K=True` | ✅ 通过 |
| **T2.10（新增，真 bug）** | 识别输出槽类型 | 无异常 | `'_SourceState' object has no attribute 'set'` → 应传 `st.slot` | ✅ 通过 |
| **T2.11（新增，真 bug）** | 关页后 agent 是否僵死 | 仍能响应 | 修复前：关页触发看门狗回收 → 从非 executor 线程 `destroy_subscription` → **与 executor 死锁**（端口 LISTEN 但 `Recv-Q=20`、日志停在“回收失联观看者”）；改为“引用计数只改状态 + 2Hz ROS timer 在 executor 线程幂等同步”后：开流→断开→12s 后 `/api/ping` 仍即时响应、`Recv-Q=0` | ✅ 通过 |

> 视频帧率说明：测得源 `/camera/color/image_raw` 仅 **3.2Hz**（假数据源发 921KB 图像的 DDS 开销），
> MJPEG 输出 3.0fps —— **几乎 1:1，WebUI 侧无瓶颈**。真机相机 30Hz 时按 `video_fps`（默认 10）输出。

---

## S3. 控制与模块启停（"能动、能干活"）

### T3.1 手动控制（摇杆 / 键盘 / 松手即停 / 看门狗）

- 做：`POST /api/cmd_vel {vx,vy,vth}` → 发布 `/cmd_vel`；前端摇杆+WASD；后端 **300ms 看门狗**：超时自动发零速。
- 命令：
  ```bash
  ros2 topic echo /cmd_vel
  # 前端按住"前进"→ 松开
  ```
- 验证：按住时 `vx>0`；**松手 0.3s 内 `/cmd_vel` 回到全零**；速度滑块上限受参数约束（默认 ≤0.3 m/s）。【通过标准】松手必停，无"飞车"。
- 不通过时：检查看门狗线程是否被阻塞；确认未与 Nav2 同时抢 `/cmd_vel`（导航中禁用摇杆或提示）。

### T3.2 机械臂面板

- 做：`POST /api/arm/goto {x,y,z,roll}` → `/goto_position`（`pose` 为 `Control`：`position` + `roll/pitch/yaw`）；`POST /api/arm/relative {dx,dy,dz}` → `/relative_position`；`POST /api/arm/home`；工作空间 `X[30,335] Y[-190,190] Z[20,220]` 越界拦截；`/unlock`、`/set_zero` 需**二次确认**。
- 命令：
  ```bash
  curl -X POST localhost:8080/api/arm/goto -d '{"x":200,"y":0,"z":130}'
  ros2 topic echo /arm_controller/position_info --once
  curl -X POST localhost:8080/api/arm/goto -d '{"x":500,"y":0,"z":130}'   # 越界
  ```
- 验证：第一条后 `position_info` 接近 (200,0,130)（±5mm）；第二条被**拒绝并提示越界**，机械臂不动。【通过标准】越界永不透传。
- 不通过时：确认字段写在 `req.pose.*`（不是顶层 `req.*`）；`goto_position` 自带螺旋就近修正，注意区分"到位"与"被修正到替代点"。

### T3.3 夹爪面板

- 做：`POST /api/gripper {close:bool}` → `/gripper/grip`；显示 `/gripper/state` 脉宽与开度%。
- 命令：
  ```bash
  curl -X POST localhost:8080/api/gripper -d '{"close":true}'
  ros2 topic echo /gripper/state --once
  ```
- 验证：服务返回 success；脉宽 2000；界面 1s 内同步为"抓紧"。【通过标准】状态与实际动作一致（动作耗时 ≥1.5s，需等待窗口）。
- 不通过时：确认 `/dev/ttyGripper` 存在（CH340 转接板曾烧毁，硬件问题需换板）。

### T3.4 导航面板（点击设目标 / 航点列表 / 取消 / 返航）

- 做：`POST /api/nav/goal {x,y,yaw}` → action `/navigate_to_pose`；`POST /api/nav/cancel`；`POST /api/nav/home`；航点列表读 `harvest_config.yaml` 的 `waypoints`（如"第一排葡萄架起点"）。
- 命令：
  ```bash
  ros2 action list | grep navigate_to_pose
  ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
    "{pose: {header: {frame_id: 'map'}, pose: {position: {x: -1.442, y: 0.232, z: 0.0}, orientation: {z: 0.012, w: 1.0}}}}"
  ```
- 验证：给点后车动；到位后界面坐标与目标误差 < 0.1 m；`cancel` 后立即停；**先决条件**：定位已初始化（`map→base_footprint` 有 TF，否则 lidar_loc 不会工作）。【通过标准】三个动作（去/取消/返航）都可重复执行不卡死。
- 不通过时：项目已知坑速查——`server_timeout` 单位是毫秒（要 2000）；`min_vel_x` 为 0 时"目标在正后方转不过去"；local costmap 无数据需 `always_send_full_costmap`。

### T3.5 `ProcessManager` — 模块单独启停（白名单）

- 做：`config/modules.yaml` 定义模块（固定参数，不接受前端任意字符串）：
  | 模块 | 命令 | 环境 | 依赖 | ready 判据 |
  |---|---|---|---|---|
  | `base` | `ros2 launch rei_robot_base base.launch.py` | `REI_ROBOT=fox_three` | — | `/odom` ≥10Hz |
  | `lidar` | `ros2 launch ydlidar_ros2_driver ydlidar_launch.py` | — | — | `/scan` ≥5Hz；启动前 `pkill -f ydlidar` |
  | `nav` | `ros2 launch fox_navigation_ros2 fox_navigation.launch.py open_rviz:=false` | `REI_ROBOT=fox_three` | base,lidar | `/map` 有数据 |
  | `camera` | `ros2 launch orbbec_camera astra_pro_plus.launch.py color_info_url:=file:///home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml ...` | — | — | `/camera/color/image_raw` ≥5Hz |
  | `arm` | `ros2 launch arm_controller arm_controller.launch.py` | — | — | `/arm_controller/position_info` ≥5Hz |
  | `gripper` | `ros2 run gripper_control gripper_node.py` | — | — | `/gripper/state` 存在 |
  | `harvest` | `ros2 launch fox_grape_harvest grape_harvest.launch.py` | — | nav,camera,arm,gripper | `/grape_harvest/status` |
  - 启动：`Popen(start_new_session=True)`；停止：`SIGINT` 到**进程组** → 3s → `SIGTERM` → `SIGKILL`；日志按模块落盘 + 实时推送前端。
- 命令：
  ```bash
  curl -X POST localhost:8080/api/modules/lidar/start
  ros2 topic hz /scan
  curl -X POST localhost:8080/api/modules/lidar/stop
  pgrep -f ydlidar_ros2_driver || echo "已停止"
  ```
- 验证：启动后 `ros2 topic hz /scan` 有稳定频率；停止后进程消失、页面状态变"已停止"；**依赖未满足时点启动 harvest 会被拒绝并提示缺哪些模块**。
- 【通过标准】① 启动相机后 `ros2 topic echo /camera/color/camera_info --once` 的 **fx ≈ 607**（证明用了正确内参）；② 重复启停 3 次无残留进程；③ 日志面板能看到该模块输出。
- 不通过时：`ros2 launch` 对 `SIGINT` 才优雅退出（别直接 kill）；ydlidar 残留会导致 `Unknown error`。

### T3.6 `harvest_node` 受控化 + 状态上报

- 做：加参数 `start_on_boot:=false`（默认不自动跑，去掉/替换现有 2s 自动启动逻辑）；新增服务/话题触发开始/暂停/取消；发布 `/grape_harvest/status`（阶段、当前航点、检测数、成功数）。
- 命令：
  ```bash
  ros2 launch fox_grape_harvest grape_harvest.launch.py
  # 观察：不自动开始
  curl -X POST localhost:8080/api/task/start
  ros2 topic echo /grape_harvest/status
  ```
- 验证：启动后 10s 内无采摘动作；`start` 后才进入流程；status 阶段字段推进（导航→检测→抓取→放篮）。【通过标准】默认不动是"安全默认"。
- 不通过时：确认 `install/fox_grape_harvest` 已重编（改动不重编不生效）。

### T3.7 任务触发：一键全流程 + 单颗点选抓取

- 做：`POST /api/task/start` 跑配置航点全流程；检测列表每条的 `[抓取]` → `POST /api/task/pick_one {detection_id}`（复用 `grape_grasp_test` 的过渡点→补偿点→夹紧→放篮流程）。
- 命令：
  ```bash
  curl -X POST localhost:8080/api/task/pick_one -d '{"id":0}'
  ```
- 验证：单颗抓取成功（葡萄被夹住并放入车上篮子）；全程可在页面看到阶段与日志。【通过标准】连续抓 2 颗不出现坐标错乱。
- 不通过时：核对 `arm.tool_offset_*` 与 `car_basket.position`；深度/手眼链路回归（S2 T2.3/T2.6）。

**阶段验收（S3 端到端）**
1. 页面依次启动 base→lidar→nav→camera→arm→gripper→harvest，全部变绿。
2. 摇杆把车开出 30cm，松手停；地图位置同步更新。
3. 地图点一个目标点 → 导航到位；点"取消"→ 停。
4. 机械臂输入 (200,0,130) → 到达；输入越界值 → 被拒。
5. 夹爪"抓紧/松开"各一次，状态面板同步。
6. 检测列表点"抓取一颗" → 成功。

| 任务 | 验证命令 | 期望结果 | 实测结果 | 结论 |
|---|---|---|---|---|
| T3.1 | 页面按住 ↑ / 松手 | 松手 0.3s 归零 | 按住 0.7s：`manual{vx:0.15,vth:0,active:true}`、`/cmd_vel` 收到 `vx=0.15`；松手 0.8s：`manual` 全零 `active:false`、假底盘日志 `vx=0.15 → vx=0.0`；专项测超时：`reason:'timeout'` | ✅ 通过 |
| T3.2 | goto (150,0,150) / 微调 / 越界 Z=999 / 解锁 | 到位 / 拒绝 / 二次确认 | `state.arm=(150,…,150)`，假服务日志 `goto_position -> (150,0,150)`；X+10 → `(160,…)` `relative_position`；Z=999 返回 `超出工作空间: Z (X[30,335] Y[-190,190] Z[20,220])` 且机械臂不动；解锁返回 `✓ 已解锁` | ✅ 通过 |
| T3.3 | 点"松开"/"抓紧" | 2000/500 同步 | 松开 → `{"ok":true,"message":"pulse=500"}`，`state.gripper={pulse:500,ratio:1.0,closed:false}`；面板 1s 内同步 | ✅ 通过 |
| T3.4 | 地图点选 → 前往 / 设初始位姿 / 清除 | 目标下发、无 Nav2 时报错 | 浮条显示 `(-0.40, 2.35)`；`前往` → `⚠ 导航未就绪（Nav2 未启动或未激活）`（预期，sim 无 Nav2）；`设初始位姿` → `✓ 已发送`；`✕` → 浮条消失且导航面板同步清空；航点下拉读到"第一排葡萄架起点/终点" | ✅ 通过（真机需 Nav2 在线复验） |
| T3.5 | 模块启停 | 无残留、fx≈607 | 见下方"T3.5 实测" | ✅ 通过（硬件项待现场） |
| T3.6 | 启动 harvest | 不自动跑 | 见下方"T3.6 实测" | ✅ 通过 |
| T3.7 | pick_one | 抓取成功 | 见下方"T3.7 实测" | ✅ 链路通过（真实抓取待硬件） |
| T3.8 | 补偿：点 `+10` / 手输 / 保存 / 撤销 | 立即生效 + 写回配置文件且注释不丢 | 见下方"T3.8 在线抓取点补偿" | ✅ 通过（真实抓取用新补偿待硬件） |

**T3.5 实测（`selftest` 模块做的无硬件端到端）**

| 检查项 | 结果 |
|---|---|
| 未知模块 `POST /api/modules/foobar/start` | `{"ok":false,"error":"未知模块: foobar（只允许白名单内的模块）"}` ✅ 不接受命令字符串 |
| 依赖互锁 `POST /api/modules/harvest/start` | `{"ok":false,"error":"依赖未启动: ['nav','camera','arm','gripper']", "missing":[…]}` ✅ |
| 启动 selftest | `{"ok":true,"pid":31986,"state":"starting"}` → 6s 后 `state=running ready=True pubs=1` ✅（就绪判据=ROS 图 publisher 数） |
| 模块日志 | `/api/modules/selftest/log` 返回 `ros2 topic pub` 的 `publishing #62: …` ✅ |
| 停止 | `{ok:true,state:stopped,code:2}`，`pgrep -f "topic pub"` → 0 残留 ✅（SIGINT 到进程组） |
| **连续启停 3 轮** | 每轮 start→running、进程数恰为 1、stop→残留 0 ✅ |
| restart（停止态 / 运行中） | 两种情况都拿到新 pid 且旧进程消失 ✅ |
| 非法动作 | `POST /api/modules/selftest/boom` → HTTP 400 ✅ |
| `POST /api/modules/reload` | 重新读 YAML，`ok=true`、8 个模块 ✅ |
| 前端面板 | 8 行（状态灯 + ready 话题 + Hz + 启停 + 日志按钮）；点启动 → "运行中"；点日志 → 看到节点输出；停止 → "已停止"；nav/harvest 行下显示"依赖未启动：…" ✅ |

**T3.6 实测（无硬件：假相机 + 无 Nav2/机械臂）**

| 检查项 | 结果 |
|---|---|
| 默认不自启动 | 启动日志：`🎛 受控模式：start_on_boot=False …—— 等外部下 start 命令`；40s 内无任何动作 ✅ |
| 状态上报 | `/grape_harvest/status` 1Hz JSON：`{"state":"idle","stage":"待命","waypoints":2,...}`；WebUI `state.task` 与 `/api/task` 同步 ✅ |
| 命令 start | 状态推进：`等待相机内参 → 机械臂归位 → 导航到航点 1/2 → 2/2 → 返回地图原点 → 完成`（无 Nav2 → 每站"导航失败，跳过"，符合预期）✅ |
| **命令 stop（流程运行中）** | 发出后 **2s 内** 收到并退出：`正在停止（当前动作完成后退出）` → `idle 已停止 共摘取 0 颗（用户停止）` ✅✅ 这是本次最关键的修复 |
| pause / resume | `paused=True` 停住，`resume` 后继续走完航点 ✅ |
| 空闲时 stop | 报 `待命 — 当前没有任务在跑`（不会卡在"正在停止"）✅ |
| 重复 start | 流程运行中再发 → `已有流程在跑，忽略本次命令` ✅ |
| 非法动作 | `POST /api/task/boom` → HTTP 400 ✅ |
| 前端任务面板 | 一键采摘（二次确认）→ "运行中 / 导航到航点 1/2 / 已用时 4s"；停止 → "待命 / 已停止" ✅ |

**T3.7 实测**

| 检查项 | 结果 |
|---|---|
| 前端检测列表 | 开启识别后出现 `可抓 | X233 Y183 Z97 mm | 深度 0.61 m | 🎯 抓取` ✅ |
| 点"🎯 抓取"（动作与 `grape_grasp_test.py` 同款） | 确认框列出动作序列 → `POST /api/task/pick_one` → 返回分步结果：`到过渡点 → 到抓取点 → 夹紧 → 回安全点 → 松开` 全部 ✅；假机械臂日志逐条对应 `(120,0,60)` → `(205,82,66)` → `夹紧 2000` → `(0,-120,60)` → `松开 500` |
| 算点校验 | 葡萄 (231.9,178.3,95.8) + 旋转后的工具偏移(-26.8,-96.4,-30.0) → 抓取点 (205.1,82.0,65.8)，与手算一致 ✅ |
| 依赖 | 只要求 `arm` + `gripper` 服务就绪，**不再依赖 harvest 节点**（未启动也能抓）✅ |
| sim 环境的限制 | harvest 节点用的是**真 YOLO** 跑**合成图** → `YOLO 检测到 0 个目标`。真机（真葡萄 + 手眼标定）才会真正夹到 → **现场复验** |
| 安全性 | 点选目标超出工作空间时按钮禁用（`reach===2`）；抓取中不允许多任务（`grasping` 防重入）；急停期间拒绝抓取 ✅ |

**S3 实施记录（T3.5–T3.7）**

- 新增后端 `fox_webui/process_manager.py` + 配置 `config/modules.yaml`（8 个模块：base/lidar/nav/camera/arm/gripper/harvest/selftest）；API：`GET /api/modules`、`POST /api/modules/{name}/{start|stop|restart}`、`GET /api/modules/{name}/log`、`POST /api/modules/reload`。
- 新增前端 `ModulePanel.js`（模块行 + 日志窗）、`TaskPanel.js`（一键采摘/暂停/继续/停止 + 进度）；`VideoPanel.js` 检测列表加 `🎯 抓取`。
- `control.py` 加 `/grape_harvest/command` 发布者与 `task_command()`；`state.py` 订阅 `/grape_harvest/status` → `state.task`；API `POST /api/task/{start|stop|pause|resume|pick_one}`（无订阅者时明确提示"先在模块启停里启动 harvest"）。
- `harvest_node.py` 受控化：`start_on_boot`(默认 false)、命令话题、状态话题、协作式取消/暂停、`pick_one`（按页面坐标挑最近的检测框，复用同一条抓取路径）；`arm/chassis_interface` 的等待改为 `wait_utils`（外部 spin 感知）。
- 新增脚本：`scripts/test_task_flow.py`（任务流冒烟）、`scripts/nested_spin_probe.py`（嵌套 spin 最小实验，用于证实下面的线程问题）。

**⚠️ 本轮发现并修掉的 3 个真 bug**

1. **`harvest_node` 的 `camera_info` QoS 不兼容**（与 S2 在 WebUI 修过的是同一类）：订阅用默认 RELIABLE，而 Orbbec/假相机发 BEST_EFFORT → 一条都收不到 → 流程卡在"等待相机内参"后终止。启动日志实证：`New publisher discovered on topic '/camera/color/camera_info', offering incompatible QoS`。改为 `qos_profile_sensor_data` 后消失。
2. **嵌套 spin 导致 stop 失效（最严重）**：原实现把整条采摘流程跑在 timer/命令回调里，等待用 `rclpy.spin_once` / `spin_until_future_complete`。最小实验（`nested_spin_probe.py`）证实：**回调内做 10 次 `spin_once(0.9)` 期间外部发的 3 条消息只被处理 1 条**。后果：流程一旦跑起来，`stop/pause` **完全收不到**，只能杀进程。修复：`MultiThreadedExecutor(3)` 主线程常驻 spin + 流程移到 worker 线程 + `wait_utils.wait_future()`（`add_done_callback + Event.wait`，不自己 spin）。修后 `stop` 2s 内生效。
3. **检测列表只在"本页点过开启识别"后才拉数据**：页面刷新后（或从另一台设备开启识别）本页列表永远不出现 → `🎯 抓取` 按钮够不着。改为每次轮询都以服务端 `enabled` 为准。
4. **子进程环境缺 `ROS_DISTRO` → 模块一点就失败**：模块日志显示 `KeyError: 'ROS_DISTRO'`（orbbec 的 `astra_pro_plus.launch.py` 直接读它）。Agent 是用 `fox_webui_env.sh` 拉起来的、不过 setup.zsh，因此必须在子进程环境里补 `ROS_DISTRO/ROS_VERSION/ROS_PYTHON_VERSION`。修后真机相机成功启动：`Initialize device cost 2066 ms`，`/camera/color/camera_info` 30Hz ✅
5. **就绪判据对"按需订阅"话题永远不满足**：`/camera/color/image_raw` 只在有人看视频时才被订阅，健康表里恒为 0Hz，于是 `min_hz` 检查永远不过 → 模块卡在"启动中"。改为：**只有收到过真实样本才用频率判据，否则只认 ROS 图（publisher 数）**。
6. **Agent 重启后模块子进程失联 → 重复实例**：子进程 `start_new_session=True` 脱离会话所以活得很好（这是想要的），但 Agent 重启后 UI 显示"已停止"，再点启动就变成两个相机实例（实测）。修：加 `detect` 模式（`pgrep -f`）识别遗留实例 → 状态显示 `外部实例` + 阻止重复启动 + 点"停止"可清理它（实测 2 个遗留实例 → 清理后 0）。

**T3.5 补充实测（真硬件相机）**

| 检查项 | 结果 |
|---|---|
| 启动 camera 模块（真机 Orbbec Astra Pro Plus） | `Initialize device cost 2066 ms` → `state=running ready=True` ✅ |
| 内参来源 | 日志 `camera calibration URL: file:///home/ubuntu/ros2fox/calib_data/color/color_camera_info.yaml`（用的是标定文件，不是旧内参）✅ |
| `/camera/color/image_raw` 实际帧率 | `ros2 topic hz` → 15.9~17.3 Hz ✅ |
| `/camera/color/camera_info` | 30.5 Hz ✅ |
| 遗留实例处理 | Agent 重启后检测到 `external_pids [42363, 43429]` → 启动被拦并提示 → 点停止 → `已清理外部实例` → 进程数 0 ✅ |

**新增开发脚本**

| 脚本 | 用途 |
|---|---|
| `scripts/dev_restart.sh` | 一键杀旧进程 → 起 agent + 假数据 → 自检 ping/状态摘要（`--no-fake` 只起后端） |
| `scripts/bench_viewers.sh` | 观看者数量 → agent CPU/RSS 基准 |
| `scripts/test_task_flow.py` | 任务流冒烟：start/stop/pause/resume/pick_one 全链路 |
| `scripts/nested_spin_probe.py` | 嵌套 spin 最小复现（证明回调内 spin 会丢消息） |
| `scripts/check_templates.mjs` | **免浏览器验证前端模板**：`node scripts/check_templates.mjs` → 10 个组件模板全部编译通过/失败。改前端后先跑它，比在无头环境里翻浏览器日志快得多 |

**⚠️ 启动方式相关的两个坑（2026-09-20 用户实测反馈）**

1. `ros2 launch fox_webui webui.launch.py` 原本**必定失败**：`config/webui.yaml` 是普通 YAML（顶层 `port: 8080`），而 ROS 参数文件必须是 `/**/ros__parameters` 结构，否则报 `RCLError: Couldn't parse params file … Cannot have a value before ros__parameters at line 7`。（之前一直用 `dev_restart.sh` 直接跑可执行文件、不经参数文件，所以没暴露。）已修：参数文件改格式 + launch 改为“文件兼底 + `port:=/host:=/robot_name:=` 显式覆盖”，实测 `port:=8081` 启动成功。
2. 报 `Package 'fox_webui' not found` 是环境问题（终端没 source 本工作区）：先 `source ~/ros2fox/install/setup.zsh`，用 `ros2 pkg prefix fox_webui` 自检；另外若已有 agent 在跑（8080），launch 会端口冲突，先 `pkill -f "fox_webui_[a]gent"` 或换端口。
3. **端口冲突 + 启动慢（2026-09-20 用户实测反馈后修）**：
   * `agent_node` 启动时先做**端口预检**，冲突时直接打印中文提示 + 两种办法（pkill 旧实例 / `port:=8081`）并 `exit 1`（原来是先等 40s、再死在 uvicorn 的 `[Errno 98]` + `terminate called without an active exception`，退出码 -6 很难读）。
   * 把 `preview_detector`（会把 torch/ultralytics 拉进来）改为**懒加载**：启动耗时从 ~40s 降到 **实测 6s**，也因此端口冲突能在 1–2s 内发现。


**S3 前端实施记录（T3.1–T3.4）**

- 新增前端组件：`ManualControl.js`（3×3 方向盘 + WASD/QE/空格 + 10Hz 续期 + 松手发零）、`EstopBar`（常驻顶栏急停，锁存后变"解除急停"）、`ArmPanel.js`（XYZ 绝对移动 + ±10mm 微调 + 回安全位 + 解锁/设零点二次确认 + 夹爪状态与按钮合并进来）、`NavPanel.js`（选点/航点/取消/返航/设初始位姿）。
- `MapView.js`：点击地图 → 出浮条「🚗 前往 / 📍 设初始位姿 / ✕」并写入 `shared.js` 的 `UI.picked`，导航面板与地图共享同一个选中点。
- 清理重复：`StatusPanels` 移除"机械臂末端"只读卡（并入 `ArmPanel`），夹爪只读卡也并入 `ArmPanel`。
- 新增 CSS：`.dpad/.dbtn`（含按下高亮与禁用态）、`.slider-row`、`.coord-row`、`.row-btns`、`.divider`、`.estop`（锁存时脉冲动画）、`.map-actions`。
- 新增开发脚本：`scripts/dev_restart.sh`（一键杀旧进程 → 起 agent+假数据 → 自检 ping/状态摘要）、`scripts/bench_viewers.sh`（观看者数量 → CPU 基准）。

**⚠️ 本轮顺带修掉的真 bug（视频名额被孤儿观看者占满）**

- 现象：页面显示视频时控制台报 `GET /video/color 503`；`/api/health` 的 `video_viewers` 显示 `{'color': 3}` 恒定不为 0 —— 反复刷新页面几次后**视频永久不可用**。
- 根因：① 纯引用计数 + 超限直接 503；② 浏览器**刷新**页面不会主动断开旧的 MJPEG 请求，socket 也不报错，旧生成器继续取帧；③ Starlette 1.6.0 在 ASGI 2.4 下走 `await stream_response(send)`（不做 `listen_for_disconnect`），所以断开检测只能靠 send 报 `OSError`，而刷新场景不会触发。结果 3 个孤儿占满名额。
- 修复：① 用 `_Viewer` 句柄替代纯计数，**名额满时踢掉最旧的连接**（新页面永远可用，不再 503）；② 每源一份 JPEG 编码缓存（同一帧多观看者复用），观看者数增加不再线性增加 CPU。
- 实测（`bench_viewers.sh`，假相机 3Hz）：0 观看者 CPU 24.0% / 1 → 26.6% / 2 → 27.2% / 3 → 31.2%，RSS 稳定 ~317MB；连续 `curl` 拉流 6 次全部 HTTP 200；浏览器连续刷新 4 次全部 200 且 `<img>` 拿到真实 640×480。
- ⚠️ 试过又回退的方案：在生成器里调 `request.is_disconnected()`。Starlette 的实现是"已取消的 CancelScope + `await receive()`"，既可能与 Starlette 抢同一个 `receive` 通道，也可能把 `Cancelled` 抛进生成器导致页面卡在 Loading —— **不要再加**。
- 已知限制：刷新留下的孤儿流最长会活到被"第 4 个观看者"顶掉（上限恒为 3）。彻底做法是给观看者加 sid + 前端 2s 心跳（后端 5s 无心跳即回收），本项目当前不实现，记在技术文档故障排查里。


---

### T3.8 在线抓取点补偿（页面实时调 + 写回配置文件）

- 需求（2026-09-22 提出）：在「采摘任务」栏里实时调 `tool_offset_x/y/z`，**改动立即生效**；
  调好了点一下保存，就写回 `harvest_config.yaml`（**下次启动自带，不用重配**）。
  现场"抓一次看一眼再挪几毫米"的过程要从"改 yaml → 重编 → 重启"几十秒，变成"点一下就动"。
- 范围（与用户确认过）：
  1. 只做 `tool_offset_x/y/z`（抓取点补偿），不动 `transition/home/grip_delay`；
  2. **手动点"保存"才落盘**（先试抓几次，满意再写）；
  3. 不单独做"测试抓取"按钮 —— 闭环就用视频栏的 🎯 抓取。
- 做：
  - 后端 `fox_webui/compensation.py`：**行级正则替换**回写 yaml（`yaml.safe_dump` 会抹掉 76 行注释，不能用）；
    双写 `src/` + `install/`；原子写（tmp + `os.replace`）；自动 `.bak`；限幅 ±200 mm。
  - 后端 `ControlManager`：`compensation() / set_compensation() / save_compensation() / revert_compensation()`；
    改的是 `grasp_sequence()` 直接读的 `arm_cfg`，所以**下一次抓取立刻用新值**；保存后若 harvest 在听，发 `{"cmd":"reload"}`。
  - 接口：`GET/POST /api/compensation`、`POST /api/compensation/save`、`POST /api/compensation/revert`。
  - 前端 `TaskPanel.js` 新增「🎯 抓取点补偿（实时）」：3 个轴各带数字框 + `−10/−1/+1/+10` 步进，
    「💾 保存到配置 / ↩ 撤销改动 / 刷新」，脏标记"有未保存改动"、"上次保存"时间。

- 验收（对照 §5.8 验证记录）：

| 检查项 | 期望 |
|---|---|
| 点 `+10` | 输入框与 `GET /api/compensation` 的值**立即一致**（不再慢一拍）；出现"有未保存改动"；保存按钮变可点 |
| 手输数字 | 是**绝对赋值**（输 `-55` 就是 `-55`，不是"再减 55"） |
| 未保存时 | `harvest_config.yaml` 不变（磁盘值仍为旧值） |
| 点「保存到配置」 | 两个文件都写、`diff` 只变 3 行、76 行注释保留、各生成 `.bak`、脏标记消失 |
| 点「撤销改动」 | 回到磁盘值，脏标记消失（不碰文件） |
| 抓取点验证 | 改补偿后 `🎯 抓取` 下发到机械臂的坐标随之改变（实测 `(205.1,82.0,65.8)` → `(206.9,96.0,75.8)`） |
| 自测收尾 | **把 `tool_offset_*` 改回现场值（−80/−60/−30）并保存，删掉 `.bak`**（别把测试值留给下一次采摘） |

- 本轮修掉的前端坑（详见技术文档 §5.8「前端这块踩的三个坑」）：
  1. `:value` 单向绑定在数字框上不刷新 → 改 `v-model` + 本地 `reactive` + **每次改动后强制拉一次接口对齐**；
  2. 轴名混用（本地 `x/y/z` vs 接口 `dx/dy/dz` vs 绝对 `tool_offset_*`）→ 点击发 `{x:10}` 被后端静默忽略 → 三者分开命名；
  3. 响应丢失时界面静默（机器满载时实测一次）→ `postJSON` 显示响应片段，并重拉一次自动对齐；
  4. 保存提示里两个文件路径尾部相同看不出区别 → 显示为 `源码 src/… 与 install/…`；
  5. 「撤销改动」的确认框是多余的（只丢内存值、不碰文件）→ 去掉。


---

## S4. 多机聚合（"一屏看多台"）

> **方案定稿（2026-09-30）**：多机主推 **模式 C（对称 HTTP）**——每台机都跑 Agent，各机之间用 HTTP
> 互拉 `/api/state`，于是**任意一台的 `:8080` 都能看到全部机器**（依据：技术文档 §3.2 四形态对照、§7.4 详解）。
> 原"模式 A（多 domain）/模式 B（Zenoh）"降级为**可选形态**（见文末"S4-附"）。

### T4.0 三台机防串台（前置，必须）

- 做：每台机启动前 `export ROS_LOCALHOST_ONLY=1`（写进各机启动脚本/`~/.zshrc`）。
- 命令（在每台机上）：
  ```bash
  export ROS_LOCALHOST_ONLY=1
  ros2 topic list | head
  ```
- 验证：三台机同时开机、同时跑导航，任一台上 `ros2 topic hz /odom` **只有 1 个发布者（本机）**，车速/位置互不影响。【通过标准】跨机零串扰。
- 不通过时：确认每台机都设了；确认没有和 `ROS_DOMAIN_ID` 混搭（模式 C 用 `LOCALHOST_ONLY` 即可）。

### T4.1 `peers.py` — 邻居 HTTP 聚合器

- 做：新增 `fox_webui/peers.py`：一个 **daemon 线程**，按 `peer_hz` 轮询每个邻居的 `GET /api/state`，
  写入 `store.update_robot(name, snapshot)`；失败则 `store.mark_offline(name)`。
  **只拉一层、绝不递归**；**只用 `requests`，绝不碰 rclpy**。
- 命令：
  ```bash
  curl -s localhost:8080/api/state | python3 -c "import json,sys;print(list(json.load(sys.stdin).get('robots',{})))"
  ```
- 验证：`robots` 键含本机 + 所有邻居名；邻居挂掉后 5s 内该机标记离线**且不报错、不影响本机数据**。
- 不通过时：邻居 URL 必须写**局域网 IP**（不能 `localhost`）；确认 `requests` 已安装。

### T4.2 `state.py` / `agent_node.py` — 支持 `peers` 参数

- 做：`state.py` 增加 `store['robots']`（本机 + 邻居合并），`snapshot()` 向后兼容；
  `agent_node.py` 声明 `peers`(list) / `peer_hz` / `peer_timeout` 参数，端口检查通过后再启动 `PeerAggregator`。
- 命令：
  ```bash
  ros2 launch fox_webui webui.launch.py robot_name:=bot1 \
      peers:="[{name: bot2, url: 'http://192.168.1.12:8080'}]"
  curl -s localhost:8080/api/state | python3 -m json.tool | grep -A4 '"robots"'
  ```
- 验证：本机与邻居数据都在 `robots` 里，**本机数据仍是实时高频**（不被邻居超时拖累）。
- 不通过时：确认聚合线程是独立 daemon 线程，未阻塞 rclpy 线程。

### T4.3 前端多机：机器下拉 / 切换 / 控制转发 / 视频直连

- 做：顶栏加**机器下拉**（`S.robots` 的键）；切换后所有面板改用该机数据；
  控制类请求改发到 `/api/to/{name}/{原路径}`（本机 Agent 用 `requests` 转发给目标 Agent，**目标机用自己的 rclpy 执行**）；
  视频源在切到邻居时直接用 `http://<邻居IP>:8080/video/{src}`。
- 命令：在 bot1 打开页面，下拉切到 bot2，点"抓紧"。
- 验证：① 切到 bot2 后页面数值 = bot2 的值；② 控制作用于 bot2（在 bot2 侧日志确认）；③ 切回 bot1 立即恢复；④ 未选中机器不拉视频（对方 `/api/health` 的 `video_viewers` 为 0）。【通过标准】三台可任意切换控制，页面不卡。
- 不通过时：确认控制转发走"本机 Agent → 目标 Agent"（不要浏览器直连邻居，避免 CORS 与鉴权分叉）。

### T4.4 对称验证（每台都能看全部）

- 做：三台机都起来后，分别在 bot1 / bot2 / bot3 的 `:8080` 打开页面。
- 命令：
  ```bash
  for ip in 11 12 13; do curl -s http://192.168.1.$ip:8080/api/state \
      | python3 -c "import json,sys;print(sorted(json.load(sys.stdin)['robots']))"; done
  ```
- 验证：三台输出的 `robots` 键集合**完全相同**（都是 3 个）。【通过标准】"打开哪台都一样（界面相同、数据相同）"。
- 不通过时：检查 `peers` 是否**互相**配齐（A 配 B/C、B 配 A/C、C 配 A/B）。

**阶段验收（S4 端到端，方案 C）**
1. 三台机都设 `ROS_LOCALHOST_ONLY=1`，都起 Agent（`peers` 互相配齐）。
2. 在**任意一台**的 `:8080` 都能看到三台状态，数值归属正确、不串台。
3. 下拉切到另一台 → 视频出图、控制生效。
4. 关掉其中一台 Agent → 另外两台 5s 内把该机标"掉线"，且**自身页面不受影响**。

| 任务 | 验证命令 | 期望结果 | 实测结果 | 结论 |
|---|---|---|---|---|
| T4.0 | 各机 `topic list` / 数据归属 | 无串扰 | 三台各占独立 `ROS_DOMAIN_ID`(61/62/63)，电压分别 24.5/22.1/19.3 V，**互不串台**；每台只看到本机发布者 | ✅ 通过 |
| T4.1 | `/api/state` → `robots` | 含本机 + 邻居 | `['bot1','bot2','bot3']`，邻居条目含 `reachable/online/url/err/age`，**scan/plan/health 已剔除**（紧凑） | ✅ 通过 |
| T4.2 | 带 `peers:=` 启动 | 合并且本机实时 | 三台顶层 `battery.voltage` 恒等于各自机器人（24.5/22.1/19.3）→ **向后兼容**；`snapshot()` 顶层字段一个未动 | ✅ 通过 |
| T4.3 | 切换 + 控制 + 视频 | 生效、不卡 | 下拉切到 bot2 → 标题 `bot1 → bot2`、电池卡显示 **22.10 V**；切回本机 → **24.50 V**。所有面板请求自动改走 `/api/to/bot2/...`（实测抓到 `state/detections/modules/compensation/health/logs` 六类）；视频源自动换成 `http://127.0.0.1:8081/video/color` | ✅ 通过 |
| T4.4 | 三台页面互看 | `robots` 集合相同 | 从 :8080/:8081/:8082 分别取 `/api/state`，`robots` 键集合**完全相同**（都是 3 个）；三台数据归属正确、**零混淆** | ✅ 通过 |

**S4 实施记录（2026-09-30）**

改动文件：

| 文件 | 改动 |
|---|---|
| `fox_webui/peers.py` | **新增**：`parse_peers()` + `PeerAggregator`（邻居采集 daemon 线程）+ stdlib `http_request/http_get_json`（**不引入新依赖**） |
| `fox_webui/state.py` | 新增 `_peers/_peer_state` + `set_peers/update_robot/mark_offline/peers_status/_robots_index`；`snapshot()` 增加 `robots`（**顶层字段完全不变**） |
| `fox_webui/webapi.py` | 新增 `GET /api/robots`、`POST/GET /api/to/{name}/{path}`（单跳转发 + 三重护栏）；`create_app(peers=…)` |
| `fox_webui/agent_node.py` | 新参数 `peers` / `peer_hz` / `peer_timeout`（默认空 = 单机）；启动横幅打印邻居 + 防串台提醒 |
| `config/webui.yaml` | 新增 `peers: ""` / `peer_hz: 5.0` / `peer_timeout: 1.0` + 三机示例与防串台说明 |
| `launch/webui.launch.py` | 支持 `peers:=` / `peer_hz:=` / `peer_timeout:=` 覆盖；文件头补模式 C 用法 |
| `web/js/shared.js` | 新增 `UI.robot` + `meName/curName/isMe/cur()/api()/videoSrc()/robotsList()` |
| `web/js/components/RobotPicker.js` | **新增**：顶栏机器下拉（可达/在线两态、掉线只标灰不删除） |
| `web/js/components/*.js` | 各面板 `S.data.X` → `cur().X`、`postJSON('/api/…')` → `postJSON(api('/api/…'))`；MapView 改为按机器单独拉 `/api/state`（邻居的 scan/plan 不在 SSE 里）；LogPanel/ModulePanel/TaskPanel 切机器时重置 |
| `web/style.css` | `.robot-picker` 样式 + `.dot.warn` |
| `main.js` | 挂载 `RobotPicker`；标题显示 `本机 → 正在看的机器`；顶栏区分"在线 / 无底盘数据 / 邻居不可达" |

**⚠️ 本轮发现并修掉的 4 个真 bug**

1. **从启动起就连不上的邻居不出现在下拉里** —— `_robots_index()` 原本遍历"收到过快照的邻居"，导致配置了但连不上的机器连名字都看不到，用户会以为 `peers` 没生效。改为遍历**登记过的全部邻居**。
2. **`online` 语义混用 → "本机离线、邻居在线"的误导** —— "本机"的 `online` 取"底盘数据在跑"，而"邻居"的 `online` 取"Agent 可达"，两者不同义。改为拆成两个字段：`reachable`（能否连上 Agent，决定能否切过去看）与 `online`（该机机器人数据是否在跑，决定绿灯）；且**不可达时 `online` 恒为 false**（旧快照只当"最后已知状态"）。
3. **转发会把 `/api/stream`（无限 SSE 流）按在 `urllib` 里读到超时** —— 已在 `/api/to/` 护栏里显式拒绝 `api/stream` 与任何 `api/to/` 前缀（后者同时天然阻断 A→B→C 递归）。
4. **SSE 里的邻居条目缺 `age`** —— 下拉只能显示"（不可达）"而无法显示"多少秒前"。已在 `_robots_index()` 补上。

**转发护栏实测**

| 用例 | 结果 |
|---|---|
| `GET /api/to/bot2/api/ping` | `200` ✅ |
| `POST /api/to/bot2/api/cmd_vel` | `{"ok":true,"cmd":[0.1,0.0,0.0]}` ✅（POST 转发生效） |
| `GET /api/to/bot2/api/health` | 透传 14 个话题 ✅ |
| `GET /api/to/nobody/api/ping`（未知邻居） | `404` ✅ |
| `GET /api/to/bot2/index.html`（非 api 路径） | `400` ✅ |
| `GET /api/to/bot2/api/stream`（流式） | `400` ✅ |
| `GET /api/to/bot2/api/to/bot1/api/ping`（递归） | `400` ✅ |

**邻居掉线实测**

| 步骤 | 结果 |
|---|---|
| 三台都在跑 | `bot1/bot2/bot3` 全部 `reachable=True online=True`，电压 24.5/22.1/19.3 ✅ |
| 杀掉 bot3 | bot3 → `reachable=False online=False err='urlopen error [Errno 111] Connection refused'`；**bot1/bot2 不受影响**，本机 `battery=24.5 twist={0.15,0.02,0.3}` 继续正常 ✅ |
| 下拉显示 | `★ bot1` / `bot2` / `bot3（不可达）`，绿灯 → 灰灯 ✅ |

> 本机模拟三台的方法：`ROS_DOMAIN_ID=61/62/63` 各起一份 `fake_telemetry.py --voltage …` + 一份 Agent
> （端口 8080/8081/8082，`peers` 互相配齐）。因为没有三台硬件时这是唯一能验证"数据归属不混淆"的办法。

**性能优化记录（2026-10-01）—— 修掉一个早就存在的卡顿根因**

现象：多机落地后页面明显卡顿、延迟极高。实测定位到元凶**不在多机代码里**，而在一条早就存在的热路径：

| 测量项 | 优化前 | 优化后 |
|---|---|---|
| `ProcessManager.status()` 一次 | **89.34 ms** | **0.001 ms** |
| └ 8× `pgrep` 子进程 | 346 ms（单次 40 ms） | 已删除（改 `/proc` 扫描，~1 ms） |
| SSE 10Hz 占事件循环 | **924 ms/秒（≈92%）** | **~0** |
| `/api/state` 往返（本机） | 796~1471 ms | **7~281 ms** |
| `/api/state` 往返（+1 邻居） | 141~618 ms | **15~42 ms** |
| `/api/ping` 往返 | 5~297 ms | **2~25 ms** |
| `/api/state` 载荷（+1 邻居） | 13982 B (+63%) | **10414 B (+22%)** |
| └ 其中 `robots` | 6043 B（42%） | **2645 B（24%）** |
| 跨机邻居拉取 | 完整 `/api/state` 8.6~14 KB × 5Hz = **43~70 KB/s** | `/api/peer_state` 1.7 KB × 5Hz = **8.4 KB/s** |

改动：

1. `process_manager.py`：状态刷新捾到**后台 1Hz 线程**（`_start_refresher`），`status()` 只读缓存；
   启停/重载时 `_invalidate()` 让缓存立即失效；`_scan_external` 由 `pgrep` 改为**遍历 `/proc/*/cmdline`**。
2. `webapi.py`：新增两个轻量端点 —— `/api/map_state`（pose/scan/plan，1.1 KB）
   与 `/api/peer_state`（邻居专用，1.7 KB）；`/api/to/` 代理超时 5s → **2s**。
3. `peers.py`：采集改拉 `/api/peer_state`（对方是旧版 Agent 时自动回退 `/api/state` 并记住）。
4. `state.py`：紧凑视图再剔除 `modules`。
5. 前端：MapView 改走 `/api/map_state`（并把它拿到的激光/路径点数分享给状态卡）；
   ModulePanel 改成自己 1Hz 拉 `/api/modules`（不再依赖 SSE）；`UI.mapN` 新增。

新增的**基建规矩**（写进了技术文档 §5.5）：
> 任何会被 `/api/state` / SSE 调用的函数，都必须保证是"读内存"级别的开销；
> 慢活（子进程、文件扫描、网络）一律交给后台线程。

**S4-附：可选形态（非主推，暂不做）**

| 任务 | 说明 |
|---|---|
| T4-A 模式 A（多 domain） | `center_node.py` 多 `rclpy.Context`；适用"只想要一台中心看全部" |
| T4-B 模式 B（Zenoh） | `zenoh-bridge-ros2dds` + `namespace:/botX`；适用跨网段 |
| T4-C 取舍 | 见技术文档 §3.2 对照表；**不要与模式 C 混用** |

---

## S5. Zenoh / FastAPI / Three.js（跨网与增强）

### T5.1 安装 Zenoh 桥（需用户执行 sudo）

- 命令（用户执行）：
  ```bash
  sudo apt install ros-humble-zenoh-bridge-dds
  zenoh-bridge-ros2dds -h | head -20
  ```
- 验证：能看到 help 输出与版本（apt 候选为 **0.5.0**）。【通过标准】命令可用。
- 不通过时：`apt update`；确认源含 ROS 仓库。

### T5.2 多机命名空间隔离（模式 B）

- 做：每台机器人一个配置 `zenoh_botX.json5`，设 `namespace: "/botX"`；中央一条无 namespace 的桥 `-e tcp/jetson1.local:7447 -e tcp/jetson2.local:7447`。
- 命令：
  ```bash
  # 机器人侧
  zenoh-bridge-ros2dds -c ~/ros2fox/config/zenoh_bot1.json5
  # 中央侧
  zenoh-bridge-ros2dds -e tcp/jetson1.local:7447
  ros2 topic list | grep bot1
  ```
- 验证：中央能看到 `/bot1/odom`、`/bot1/scan` 等（含 `/bot1/tf`、`/bot1/rosout` 前缀）。【通过标准】前缀齐全、数值真实。
- 不通过时：确认两侧 `ROS_DOMAIN_ID`/`ROS_LOCALHOST_ONLY` 已隔离（**官方警告：被桥接的两台主机之间不能有 DDS 通信，否则重复/回环流量**）。

### T5.3 实测 action 是否跨桥（**关键风险点**）

- 做：0.5.0 版本较老，需实测 action 转发。
- 命令：
  ```bash
  ros2 action list | grep -i bot1
  ros2 action send_goal /bot1/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: ...}"
  ```
- 验证：能看到并调用 `/bot1/navigate_to_pose`。【通过标准】
  - **支持** → 中央可直接触发远端导航（架构最简）。
  - **不支持** → 记录结论，改用"**机器人本地 Agent 触发**"路径：中央只发任务指令给该机 Agent（HTTP/WebSocket），由 Agent 本地调 action。**架构已预留，不阻塞交付。**
- 不通过时：不要用"再叠一层 rosbridge 只为 action"的绕路方案（增加复杂度），优先用本地 Agent。

### T5.4 生产运行：FastAPI + uvicorn 替换开发服务器

- 命令：`uvicorn fox_webui.webapi:app --host 0.0.0.0 --port 8080 --workers 1`
- 验证：并发 3 个客户端（手机+PC+平板）同时打开，SSE 与视频都不掉。【通过标准】72 小时不崩（可选长跑）。
- 不通过时：`workers` 必须为 1（rclpy 状态在进程内，不能多进程）。

### T5.5 Three.js 3D（地图平面 + 机器人 + 机械臂）

- 做：地图平面贴图 + 机器人模型/箭头 + 机械臂简化模型（按 `/arm_controller/position_info` 实时更新关节）。
- 验证：3D 视图里机械臂跟着实际运动；帧率 ≥ 30fps（看视频时 ≥ 20fps）。【通过标准】不引入明显卡顿。
- 不通过时：几何体复用、只在数据变化时更新矩阵。

### T5.6 跨机时钟对齐（可选但推荐）

- 做：各机启用 chrony 与中央同步（或用 Zenoh HLC 时间戳）。
- 验证：`chronyc tracking` 偏差 < 50ms；多机日志时间线可对齐。【通过标准】跨机排障可用。

**阶段验收（S5 端到端）**：两台机通过 Zenoh 汇聚到中央一屏，跨网（不同网段/热点）可看可控；3D 视图可用。

| 任务 | 验证命令 | 期望结果 | 实测结果 | 结论 |
|---|---|---|---|---|
| T5.1 | `zenoh-bridge-ros2dds -h` | 可用 | | |
| T5.2 | `ros2 topic list \| grep bot1` | 前缀齐全 | | |
| T5.3 | `ros2 action list` | 支持/不支持结论 | | |
| T5.4 | 3 客户端并发 | 不掉线 | | |
| T5.5 | 3D 视图 | ≥30fps | | |
| T5.6 | `chronyc tracking` | <50ms | | |

---

## S6. 打磨与总验收

### T6.1 开机自启（systemd，可选）
- 做：`fox-webui.service`（`Restart=always`、`After=network-online.target`、带 ROS 环境）。
- 验证：`sudo systemctl restart fox-webui && systemctl status fox-webui` → active(running)；重启整机后手机可直接访问。
- 【通过标准】异常退出能自动拉起。

### T6.2 手机适配 + 二维码入口
- 做：响应式（竖屏堆叠、按钮 ≥ 44px）；启动时终端打印 `http://<ip>:8080` 二维码。
- 验证：iOS/Android 各测一次；单手可完成"看状态→点导航→急停"。
- 【通过标准】横竖屏都不出现横向滚动条。

### T6.3 日志面板增强
- 做：分级/关键字/模块过滤、导出 `.txt`、崩溃时自动抓取最近 200 行。
- 验证：导出文件能正常打开且时间顺序正确。

### T6.4 参数查看（默认只读）
- 做：`GET /api/config` 返回 `harvest_config.yaml` / `nav2_params.yaml` 关键项；编辑功能默认关闭，开启后写回并提示"需重启对应模块"。
- 验证：改一个无关紧要的参数（如 `yolo_confidence`）重启模块后生效。
- 【通过标准】只读默认；写操作有二次确认 + 备份原文件。

### T6.5 性能压测与限流
- 做：把视频/状态/YOLO 频率做成可配；给出"低配/标准/高配"三档预设。
- 验证：标准档下 WebUI 总 CPU < 25%（不看视频 < 5%）；导航期间 `Control loop missed its desired rate` **不出现**。
- 【通过标准】加入 WebUI 后导航行为与不加时一致。

### T6.6 最终端到端验收（8 项场景）
| # | 场景 | 通过标准 |
|---|---|---|
| 1 | 冷启动：一键启动全部模块 | 全绿，日志无 ERROR |
| 2 | 状态面板 | 机械臂/电池/坐标/速度/夹爪全部正确 |
| 3 | 视频与识别 | 三源切换正常、识别坐标 ±2cm |
| 4 | 手动控制 | 摇杆走停正常、急停有效 |
| 5 | 导航 | 点选目标可达、取消/返航正常 |
| 6 | 机械臂+夹爪 | goto/home/相对微调/开合正常 |
| 7 | 单颗抓取 | 成功抓取并放篮 |
| 8 | 一键全流程采摘 | 按航点跑完全程并返回原点 |
| 9 | 多机 | 一屏两机、切换视频、分别控制 |
| 10 | 异常恢复 | 拔掉/停掉某模块，页面 3s 内报警，重启后自动恢复 |

---

## 附录 A. 常用验证命令速查

```bash
# 环境
source /opt/ros/humble/setup.zsh && source ~/ros2fox/install/setup.zsh

# 构建（改 src 后必做）
cd ~/ros2fox && colcon build --packages-select fox_webui gripper_control fox_grape_harvest

# 接口
ros2 topic list | sort
ros2 topic hz /odom /scan /camera/color/image_raw
ros2 service list | grep -E "goto_position|gripper|home"
ros2 action list | grep navigate

# WebUI
curl -s localhost:8080/api/state | python3 -m json.tool
curl -s localhost:8080/api/health | python3 -m json.tool
timeout 3 curl -sN localhost:8080/api/stream | grep -c '^data:'
curl -sI localhost:8080/video/color | head -3

# 排障
pkill -f ydlidar                       # 雷达端口占用
diff src/fox_navigation_ros2/param/nav2_params.yaml \
     install/fox_navigation_ros2/share/fox_navigation_ros2/param/nav2_params.yaml
```

## 附录 B. 回滚点与止损

| 风险动作 | 回滚方式 |
|---|---|
| 改动 `gripper_node.py` | `git checkout -- src/gripper_control/scripts/gripper_node.py` 后重编 |
| 改动 `harvest_node.py` | `git stash` 或还原后重编 `fox_grape_harvest` |
| 切换 `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` | 取消该环境变量并重启全部节点（建议先只在 WebUI 桥接侧启用） |
| 开启 Zenoh 桥后出现重复数据 | 确认两种模式**未同时开**；关闭 Zenoh 桥回退模式 A |
| 新增包影响现有构建 | `rm -rf build/fox_webui install/fox_webui` 后单独重编 |
| 前端改坏 | 保留上一版 `web/` 目录快照（`tar` 备份） |
