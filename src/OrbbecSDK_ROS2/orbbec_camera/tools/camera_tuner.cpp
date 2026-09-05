/*******************************************************************************
* camera_tuner.cpp — Orbbec 相机调参 / 枚举工具
*
* 用途：
*   1. 枚举设备支持的所有分辨率(profile)与深度工作模式
*   2. 运行时调节深度/IR 相关参数（软滤波、LDP、激光能量、曝光、增益等）
*   3. 捕获一帧 depth/IR/color 图像保存到目录，方便对比调参效果
*   4. 把当前生效参数导出为 YAML，供更新 astra_pro_plus.launch.py
*
* 注意：运行本工具前需要先停止正在运行的相机节点（设备需独占访问）。
*
* 用法示例：
*   # 1) 仅枚举设备/profile/深度模式 + 打印当前关键属性 + 导出 YAML
*   camera_tuner --out /tmp/camera_settings.yaml
*
*   # 2) 关闭软滤波 + 关闭 LDP + 提高激光能量，并捕获一帧对比
*   camera_tuner --set soft_filter=off --set ldp=off --set laser_energy=8 \
*                --capture /tmp/tune_softoff_ldpoff_8
*
*   # 3) 恢复默认软滤波，改用更宽松的斑点参数，捕获对比
*   camera_tuner --set soft_filter=on --set speckle_size=2000 --set max_diff=10 \
*                --capture /tmp/tune_soft_on_sp2000
*
*   # 4) 切换深度工作模式（如 High Accuracy）后捕获
*   camera_tuner --depth-mode "High Accuracy" --capture /tmp/tune_highacc
*
*   --set 支持的 key：
*     soft_filter        (bool on/off)   深度软滤波开关
*     max_diff           (int)           软滤波最大深度差
*     speckle_size       (int)           软滤波最大斑点尺寸
*     ldp                (bool on/off)   LDP 开关
*     laser_energy       (int)           激光能量等级
*     laser_on           (bool on/off)   激光开关
*     ir_exposure        (int)           IR 曝光
*     ir_gain            (int)           IR 增益
*     ir_auto_exposure   (bool on/off)   IR 自动曝光
*     ir_brightness      (int)           IR 亮度
*     depth_exposure     (int)           深度曝光
*     depth_auto_exposure(bool on/off)   深度自动曝光
*******************************************************************************/
#include <libobsensor/ObSensor.hpp>
#include <opencv2/opencv.hpp>

#include <magic_enum/magic_enum.hpp>

#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

using namespace ob;
namespace fs = std::filesystem;

// 全局命令行参数
static std::vector<std::pair<std::string, std::string>> g_sets;  // --set key=value
static std::string g_depth_mode;                                 // --depth-mode
static std::string g_capture_dir;                                // --capture
static std::string g_out_file;                                   // --out
static bool g_list_only = false;                                 // --list
static bool g_d2c_list = false;                                  // --d2c-list
static bool g_align_test = false;                                // --align-test
static bool g_cam_param = false;                                 // --cam-param

static void printUsage(const char *prog) {
  std::cout << "用法: " << prog << " [选项]\n"
            << "  --list                          仅枚举设备/profile/深度模式并打印关键属性\n"
            << "  --d2c-list                      查询支持 D2C 对齐的深度分辨率列表\n"
            << "  --align-test                    测试深度-彩色对齐(软件模式)是否可用\n"
            << "  --cam-param                     打印相机内参/外参(getCameraParam)\n"
            << "  --set key=value                 设置设备属性，可多次使用（见文件头说明）\n"
            << "  --depth-mode <name>             切换深度工作模式（如 High Accuracy）\n"
            << "  --capture <dir>                 捕获一帧 depth/IR/color 保存到目录\n"
            << "  --out <file.yaml>               把当前生效参数导出为 YAML\n";
}

static bool parseBool(const std::string &v) {
  if (v == "1" || v == "true" || v == "on" || v == "yes") return true;
  if (v == "0" || v == "false" || v == "off" || v == "no") return false;
  return std::stoi(v) != 0;
}

static void printDeviceInfo(const std::shared_ptr<Device> &device) {
  auto info = device->getDeviceInfo();
  std::cout << "==================================================\n"
            << "设备信息:\n"
            << "  名称      : " << info->name() << "\n"
            << "  PID       : 0x" << std::hex << info->pid() << std::dec << "\n"
            << "  VID       : 0x" << std::hex << info->vid() << std::dec << "\n"
            << "  序列号    : " << info->serialNumber() << "\n"
            << "  固件版本  : " << info->firmwareVersion() << "\n"
            << "  连接方式  : " << info->connectionType() << "\n";
  std::cout << "==================================================\n";
}

// 打印某个 sensor 的全部 profile
static void listProfiles(const std::shared_ptr<Device> &device) {
  auto sensor_list = device->getSensorList();
  if (!sensor_list) return;
  for (size_t i = 0; i < sensor_list->count(); i++) {
    auto sensor = sensor_list->getSensor(i);
    auto type = sensor->type();
    if (type != OB_SENSOR_COLOR && type != OB_SENSOR_DEPTH && type != OB_SENSOR_IR &&
        type != OB_SENSOR_IR_LEFT && type != OB_SENSOR_IR_RIGHT) {
      continue;
    }
    auto plist = sensor->getStreamProfileList();
    std::cout << "[" << magic_enum::enum_name(type) << "] 支持的分辨率:\n";
    for (size_t j = 0; j < plist->count(); j++) {
      auto p = plist->getProfile(j)->as<VideoStreamProfile>();
      std::cout << "    " << p->width() << "x" << p->height() << " @ " << p->fps()
                << "fps  " << magic_enum::enum_name(p->format()) << "\n";
    }
  }
}

static void listDepthModes(const std::shared_ptr<Device> &device) {
  if (!device->isPropertySupported(OB_STRUCT_CURRENT_DEPTH_ALG_MODE, OB_PERMISSION_READ_WRITE)) {
    std::cout << "[深度] 当前设备不支持深度工作模式切换\n";
    return;
  }
  auto cur = device->getCurrentDepthWorkMode();
  std::cout << "[深度] 当前工作模式: " << cur.name << "\n";
  auto mode_list = device->getDepthWorkModeList();
  std::cout << "[深度] 可用工作模式:\n";
  for (uint32_t i = 0; i < mode_list->count(); i++) {
    std::cout << "    " << (*mode_list)[i].name << "\n";
  }
}

static void printIntProperty(const std::shared_ptr<Device> &device, OBPropertyID id,
                             const std::string &label) {
  if (!device->isPropertySupported(id, OB_PERMISSION_READ)) {
    std::cout << "    " << label << ": 不支持\n";
    return;
  }
  try {
    auto range = device->getIntPropertyRange(id);
    int val = device->getIntProperty(id);
    std::cout << "    " << label << ": " << val << "  (范围 " << range.min << " ~ " << range.max
              << ")\n";
  } catch (const std::exception &e) {
    std::cout << "    " << label << ": 读取失败 (" << e.what() << ")\n";
  }
}

static void printBoolProperty(const std::shared_ptr<Device> &device, OBPropertyID id,
                              const std::string &label) {
  if (!device->isPropertySupported(id, OB_PERMISSION_READ)) {
    std::cout << "    " << label << ": 不支持\n";
    return;
  }
  try {
    bool val = device->getBoolProperty(id);
    std::cout << "    " << label << ": " << (val ? "ON" : "OFF") << "\n";
  } catch (const std::exception &e) {
    std::cout << "    " << label << ": 读取失败 (" << e.what() << ")\n";
  }
}

static void printKeyProperties(const std::shared_ptr<Device> &device) {
  std::cout << "------------------------------------------\n[关键属性当前值]\n";
  printBoolProperty(device, OB_PROP_DEPTH_SOFT_FILTER_BOOL, "soft_filter   ");
  printIntProperty(device, OB_PROP_DEPTH_MAX_DIFF_INT, "max_diff      ");
  printIntProperty(device, OB_PROP_DEPTH_MAX_SPECKLE_SIZE_INT, "speckle_size  ");
  printBoolProperty(device, OB_PROP_LDP_BOOL, "ldp           ");
  printIntProperty(device, OB_PROP_LASER_ENERGY_LEVEL_INT, "laser_energy  ");
  printIntProperty(device, OB_PROP_LASER_CONTROL_INT, "laser_on      ");
  printIntProperty(device, OB_PROP_IR_EXPOSURE_INT, "ir_exposure   ");
  printIntProperty(device, OB_PROP_IR_GAIN_INT, "ir_gain       ");
  printBoolProperty(device, OB_PROP_IR_AUTO_EXPOSURE_BOOL, "ir_auto_exposure");
  printIntProperty(device, OB_PROP_IR_BRIGHTNESS_INT, "ir_brightness ");
  printIntProperty(device, OB_PROP_DEPTH_EXPOSURE_INT, "depth_exposure");
  printBoolProperty(device, OB_PROP_DEPTH_AUTO_EXPOSURE_BOOL, "depth_auto_exposure");
  std::cout << "------------------------------------------\n";
}

// 从 profile 列表中选取指定宽高的 profile（找不到则取第一个）
static std::shared_ptr<VideoStreamProfile> findProfile(const std::shared_ptr<Device> &device,
                                                       OBSensorType type, int w, int h) {
  auto sensor = device->getSensor(type);
  if (!sensor) return nullptr;
  auto plist = sensor->getStreamProfileList();
  std::shared_ptr<VideoStreamProfile> first;
  for (size_t i = 0; i < plist->count(); i++) {
    auto p = plist->getProfile(i)->as<VideoStreamProfile>();
    if (!first) first = p;
    if (w > 0 && h > 0 && static_cast<int>(p->width()) == w && static_cast<int>(p->height()) == h) {
      return p;
    }
  }
  return first;
}

// 按指定格式+宽高选取 profile，找不到则回退到 findProfile
static std::shared_ptr<VideoStreamProfile> findProfileWithFormat(
    const std::shared_ptr<Device> &device, OBSensorType type, int w, int h, OBFormat fmt) {
  auto sensor = device->getSensor(type);
  if (!sensor) return nullptr;
  auto plist = sensor->getStreamProfileList();
  for (size_t i = 0; i < plist->count(); i++) {
    auto p = plist->getProfile(i)->as<VideoStreamProfile>();
    if (p->format() == fmt && static_cast<int>(p->width()) == w &&
        static_cast<int>(p->height()) == h) {
      return p;
    }
  }
  return findProfile(device, type, w, h);
}

// 应用 --set 参数
static void applySets(const std::shared_ptr<Device> &device) {
  for (const auto &kv : g_sets) {
    const std::string &key = kv.first;
    const std::string &val = kv.second;
    try {
      if (key == "soft_filter") {
        if (!device->isPropertySupported(OB_PROP_DEPTH_SOFT_FILTER_BOOL, OB_PERMISSION_READ_WRITE)) {
          std::cout << "[跳过] 设备不支持 soft_filter\n";
          continue;
        }
        device->setBoolProperty(OB_PROP_DEPTH_SOFT_FILTER_BOOL, parseBool(val));
        std::cout << "[OK] soft_filter -> " << val << "\n";
      } else if (key == "max_diff") {
        if (!device->isPropertySupported(OB_PROP_DEPTH_MAX_DIFF_INT, OB_PERMISSION_WRITE)) {
          std::cout << "[跳过] 设备不支持 max_diff\n";
          continue;
        }
        device->setIntProperty(OB_PROP_DEPTH_MAX_DIFF_INT, std::stoi(val));
        std::cout << "[OK] max_diff -> " << val << "\n";
      } else if (key == "speckle_size") {
        if (!device->isPropertySupported(OB_PROP_DEPTH_MAX_SPECKLE_SIZE_INT, OB_PERMISSION_WRITE)) {
          std::cout << "[跳过] 设备不支持 speckle_size\n";
          continue;
        }
        device->setIntProperty(OB_PROP_DEPTH_MAX_SPECKLE_SIZE_INT, std::stoi(val));
        std::cout << "[OK] speckle_size -> " << val << "\n";
      } else if (key == "ldp") {
        if (!device->isPropertySupported(OB_PROP_LDP_BOOL, OB_PERMISSION_WRITE)) {
          std::cout << "[跳过] 设备不支持 ldp\n";
          continue;
        }
        device->setBoolProperty(OB_PROP_LDP_BOOL, parseBool(val));
        std::cout << "[OK] ldp -> " << val << "\n";
      } else if (key == "laser_energy") {
        if (!device->isPropertySupported(OB_PROP_LASER_ENERGY_LEVEL_INT, OB_PERMISSION_READ_WRITE)) {
          std::cout << "[跳过] 设备不支持 laser_energy\n";
          continue;
        }
        auto range = device->getIntPropertyRange(OB_PROP_LASER_ENERGY_LEVEL_INT);
        int v = std::stoi(val);
        if (v < range.min || v > range.max) {
          std::cout << "[警告] laser_energy " << v << " 超出范围 " << range.min << "~" << range.max
                    << "，忽略\n";
          continue;
        }
        device->setIntProperty(OB_PROP_LASER_ENERGY_LEVEL_INT, v);
        std::cout << "[OK] laser_energy -> " << val << "\n";
      } else if (key == "laser_on") {
        if (!device->isPropertySupported(OB_PROP_LASER_CONTROL_INT, OB_PERMISSION_READ_WRITE)) {
          std::cout << "[跳过] 设备不支持 laser_on\n";
          continue;
        }
        device->setIntProperty(OB_PROP_LASER_CONTROL_INT, parseBool(val) ? 1 : 0);
        std::cout << "[OK] laser_on -> " << val << "\n";
      } else if (key == "ir_exposure") {
        device->setIntProperty(OB_PROP_IR_EXPOSURE_INT, std::stoi(val));
        std::cout << "[OK] ir_exposure -> " << val << "\n";
      } else if (key == "ir_gain") {
        device->setIntProperty(OB_PROP_IR_GAIN_INT, std::stoi(val));
        std::cout << "[OK] ir_gain -> " << val << "\n";
      } else if (key == "ir_auto_exposure") {
        device->setBoolProperty(OB_PROP_IR_AUTO_EXPOSURE_BOOL, parseBool(val));
        std::cout << "[OK] ir_auto_exposure -> " << val << "\n";
      } else if (key == "ir_brightness") {
        device->setIntProperty(OB_PROP_IR_BRIGHTNESS_INT, std::stoi(val));
        std::cout << "[OK] ir_brightness -> " << val << "\n";
      } else if (key == "depth_exposure") {
        device->setIntProperty(OB_PROP_DEPTH_EXPOSURE_INT, std::stoi(val));
        std::cout << "[OK] depth_exposure -> " << val << "\n";
      } else if (key == "depth_auto_exposure") {
        device->setBoolProperty(OB_PROP_DEPTH_AUTO_EXPOSURE_BOOL, parseBool(val));
        std::cout << "[OK] depth_auto_exposure -> " << val << "\n";
      } else {
        std::cout << "[错误] 未知参数 key: " << key << "\n";
      }
    } catch (const std::exception &e) {
      std::cout << "[错误] 设置 " << key << " 失败: " << e.what() << "\n";
    }
  }
}

// 切换深度工作模式
static void applyDepthMode(const std::shared_ptr<Device> &device) {
  if (g_depth_mode.empty()) return;
  if (!device->isPropertySupported(OB_STRUCT_CURRENT_DEPTH_ALG_MODE, OB_PERMISSION_READ_WRITE)) {
    std::cout << "[错误] 设备不支持深度工作模式切换\n";
    return;
  }
  try {
    device->switchDepthWorkMode(g_depth_mode.c_str());
    std::cout << "[OK] 深度工作模式已切换为: " << g_depth_mode << "\n";
  } catch (const std::exception &e) {
    std::cout << "[错误] 切换深度工作模式失败: " << e.what() << "\n";
  }
}

// 保存一帧深度图：raw 16bit PGM + 伪彩色 PNG + 有效深度统计
static void saveDepthFrame(const std::shared_ptr<DepthFrame> &frame, const fs::path &dir) {
  uint32_t w = frame->width();
  uint32_t h = frame->height();
  float scale = frame->getValueScale();
  const uint16_t *data = static_cast<const uint16_t *>(frame->data());

  // 有效深度统计（单位 mm）
  int valid_count = 0;
  float max_mm = 0.0f;
  float min_mm = 0.0f;
  for (uint32_t i = 0; i < w * h; i++) {
    if (data[i] == 0) continue;
    float mm = data[i] * scale;
    if (valid_count == 0) {
      min_mm = mm;
    }
    if (mm > max_mm) max_mm = mm;
    if (mm < min_mm) min_mm = mm;
    valid_count++;
  }
  float valid_ratio = static_cast<float>(valid_count) / static_cast<float>(w * h) * 100.0f;
  std::cout << "[深度帧] " << w << "x" << h << " valueScale=" << scale << " 有效像素="
            << valid_count << " (" << std::fixed << std::setprecision(2) << valid_ratio
            << "%)  深度范围 " << min_mm << " ~ " << max_mm << " mm\n";

  // 保存原始 16bit 数据为 PGM
  std::ofstream ofs((dir / "depth_raw.pgm").string(), std::ios::binary);
  ofs << "P5\n" << w << " " << h << "\n65535\n";
  ofs.write(reinterpret_cast<const char *>(data), w * h * sizeof(uint16_t));
  ofs.close();

  // 伪彩色/灰度：像素值*scale = 毫米(mm)
  // 借鉴 depth_viewer.py 的自适应归一化（否则 Astra Pro 近距离深度会全挤在蓝色一档）：
  //   把有效深度实际范围拉伸到 0~255，上限封顶 5000mm，蓝=近 红=远
  float cmin = (valid_count > 0) ? min_mm : 0.0f;
  float cmax = (max_mm < 5000.0f) ? max_mm : 5000.0f;  // 上限 5 米
  if (cmax <= cmin) {  // 保护：范围无效时回退到 0~5000mm
    cmin = 0.0f;
    cmax = 5000.0f;
  }
  cv::Mat raw(h, w, CV_16UC1, const_cast<uint16_t *>(data));
  cv::Mat depth_mm;
  raw.convertTo(depth_mm, CV_32FC1, scale);  // mm
  cv::Mat disp;
  cv::subtract(depth_mm, cv::Scalar(cmin), disp);
  disp = disp * (255.0f / (cmax - cmin));  // 越界自动饱和到 0~255
  cv::Mat disp8;
  disp.convertTo(disp8, CV_8UC1);
  cv::imwrite((dir / "depth_gray.png").string(), disp8);  // 8bit 灰度图

  // 有效深度掩码（>0 视为有效）
  cv::Mat valid_mask;
  cv::threshold(depth_mm, valid_mask, 1.0f, 255.0, cv::THRESH_BINARY);
  valid_mask.convertTo(valid_mask, CV_8UC1);

  // 先全部伪彩色，再把无效区域(<=0)强制设为黑色
  // （注意：JET 色板把 0 映射成深蓝色，必须先上色再置黑，否则无效区域会显示成蓝色）
  cv::Mat color;
  cv::applyColorMap(disp8, color, cv::COLORMAP_JET);
  cv::Mat color_masked = cv::Mat::zeros(h, w, CV_8UC3);
  color.copyTo(color_masked, valid_mask);
  cv::imwrite((dir / "depth_colored.png").string(), color_masked);
  std::cout << "[深度图] 已保存 depth_colored.png(伪彩, 蓝近红远, 黑=无效) 与 "
               "depth_gray.png(灰度), 距离刻度 "
            << cmin << "~" << cmax << "mm (有效 " << valid_count << "px/" << std::fixed
            << std::setprecision(1) << valid_ratio << "%)\n";
}

static void saveIrFrame(const std::shared_ptr<IRFrame> &frame, const fs::path &dir,
                        const std::string &name) {
  uint32_t w = frame->width();
  uint32_t h = frame->height();
  OBFormat fmt = frame->format();
  cv::Mat gray;
  if (fmt == OB_FORMAT_Y8) {
    const uint8_t *d = static_cast<const uint8_t *>(frame->data());
    gray = cv::Mat(h, w, CV_8UC1, const_cast<uint8_t *>(d)).clone();
  } else {  // Y10/Y12/Y16 按 16bit 处理
    const uint16_t *d = static_cast<const uint16_t *>(frame->data());
    cv::Mat raw(h, w, CV_16UC1, const_cast<uint16_t *>(d));
    raw.convertTo(gray, CV_8UC1, 255.0 / 1023.0);
  }
  cv::imwrite((dir / name).string(), gray);
  std::cout << "[IR帧] 保存 " << name << " (" << w << "x" << h << ")\n";
}

static void saveColorFrame(const std::shared_ptr<ColorFrame> &frame, const fs::path &dir) {
  uint32_t w = frame->width();
  uint32_t h = frame->height();
  OBFormat fmt = frame->format();
  if (fmt == OB_FORMAT_RGB) {
    const uint8_t *d = static_cast<const uint8_t *>(frame->data());
    cv::Mat rgb(h, w, CV_8UC3, const_cast<uint8_t *>(d));
    cv::Mat bgr;
    cv::cvtColor(rgb, bgr, cv::COLOR_RGB2BGR);
    cv::imwrite((dir / "color.png").string(), bgr);
  } else if (fmt == OB_FORMAT_MJPG || fmt == OB_FORMAT_H264 || fmt == OB_FORMAT_H265) {
    const uint8_t *d = static_cast<const uint8_t *>(frame->data());
    cv::Mat buf(1, static_cast<int>(frame->dataSize()), CV_8UC1, const_cast<uint8_t *>(d));
    cv::Mat img = cv::imdecode(buf, cv::IMREAD_COLOR);
    if (!img.empty()) cv::imwrite((dir / "color.png").string(), img);
  } else if (fmt == OB_FORMAT_YUYV) {
    const uint8_t *d = static_cast<const uint8_t *>(frame->data());
    cv::Mat yuyv(h, w, CV_8UC2, const_cast<uint8_t *>(d));
    cv::Mat bgr;
    cv::cvtColor(yuyv, bgr, cv::COLOR_YUV2BGR_YUY2);
    cv::imwrite((dir / "color.png").string(), bgr);
  } else {
    std::cout << "[彩色帧] 不支持的格式 " << magic_enum::enum_name(fmt) << "，跳过\n";
    return;
  }
  std::cout << "[彩色帧] 保存 color.png (" << w << "x" << h << ")\n";
}

// 单流捕获一帧并保存（复用同一个 pipeline，逐个流 start/stop，避免多流带宽/兼容问题）
static void captureOneStream(const std::shared_ptr<Pipeline> &pipeline,
                             const std::shared_ptr<Device> &device, OBSensorType type, int w,
                             int h) {
  std::shared_ptr<VideoStreamProfile> profile;
  if (type == OB_SENSOR_COLOR) {
    profile = findProfileWithFormat(device, type, w, h, OB_FORMAT_RGB);
  } else {
    profile = findProfile(device, type, w, h);
  }
  if (!profile) {
    std::cout << "[跳过] 无 " << magic_enum::enum_name(type) << " 的 " << w << "x" << h
              << " profile\n";
    return;
  }
  auto config = std::make_shared<Config>();
  config->enableStream(profile);
  try {
    pipeline->start(config);
  } catch (const std::exception &e) {
    std::cout << "[错误] 启动 " << magic_enum::enum_name(type) << " 流失败: " << e.what()
              << "\n";
    return;
  }
  std::shared_ptr<FrameSet> frameset;
  for (int i = 0; i < 10; i++) {
    frameset = pipeline->waitForFrames(3000);
    if (frameset) break;
  }
  if (!frameset) {
    std::cout << "[错误] 等待 " << magic_enum::enum_name(type) << " 帧超时\n";
    pipeline->stop();
    return;
  }
  if (type == OB_SENSOR_DEPTH) {
    auto f = frameset->getFrame(OB_FRAME_DEPTH);
    if (f) saveDepthFrame(f->as<DepthFrame>(), g_capture_dir);
  } else if (type == OB_SENSOR_IR) {
    auto f = frameset->getFrame(OB_FRAME_IR);
    if (f) saveIrFrame(f->as<IRFrame>(), g_capture_dir, "ir.png");
  } else if (type == OB_SENSOR_COLOR) {
    auto f = frameset->getFrame(OB_FRAME_COLOR);
    if (f) saveColorFrame(f->as<ColorFrame>(), g_capture_dir);
  }
  pipeline->stop();
}

// 捕获一帧并保存（分单流捕获）
static void captureFrames(const std::shared_ptr<Device> &device) {
  if (g_capture_dir.empty()) return;
  fs::create_directories(g_capture_dir);
  auto pipeline = std::make_shared<Pipeline>(device);
  captureOneStream(pipeline, device, OB_SENSOR_DEPTH, 640, 480);
  captureOneStream(pipeline, device, OB_SENSOR_IR, 640, 480);
  captureOneStream(pipeline, device, OB_SENSOR_COLOR, 640, 480);
}

// 导出当前生效参数为 YAML（供 launch 使用）
static void exportYaml(const std::shared_ptr<Device> &device) {
  if (g_out_file.empty()) return;
  std::ofstream ofs(g_out_file);
  if (!ofs) {
    std::cout << "[错误] 无法写入 " << g_out_file << "\n";
    return;
  }
  ofs << "# 相机参数导出（camera_tuner 生成）\n"
      << "# 将下列参数作为 launch 参数覆盖值使用，例如:\n"
      << "#   ros2 launch orbbec_camera astra_pro_plus.launch.py \\\n"
      << "#     enable_soft_filter:=<soft_filter> soft_filter_max_diff:=<max_diff> ...\n\n";
  auto dump_bool = [&](OBPropertyID id, const std::string &key) {
    if (device->isPropertySupported(id, OB_PERMISSION_READ)) {
      ofs << key << ": " << (device->getBoolProperty(id) ? "true" : "false") << "\n";
    }
  };
  auto dump_int = [&](OBPropertyID id, const std::string &key) {
    if (device->isPropertySupported(id, OB_PERMISSION_READ)) {
      ofs << key << ": " << device->getIntProperty(id) << "\n";
    }
  };
  dump_bool(OB_PROP_DEPTH_SOFT_FILTER_BOOL, "enable_soft_filter");
  dump_int(OB_PROP_DEPTH_MAX_DIFF_INT, "soft_filter_max_diff");
  dump_int(OB_PROP_DEPTH_MAX_SPECKLE_SIZE_INT, "soft_filter_speckle_size");
  dump_bool(OB_PROP_LDP_BOOL, "enable_ldp");
  dump_int(OB_PROP_LASER_ENERGY_LEVEL_INT, "laser_energy_level");
  dump_int(OB_PROP_LASER_CONTROL_INT, "laser_on");
  dump_int(OB_PROP_IR_EXPOSURE_INT, "ir_exposure");
  dump_int(OB_PROP_IR_GAIN_INT, "ir_gain");
  dump_bool(OB_PROP_IR_AUTO_EXPOSURE_BOOL, "enable_ir_auto_exposure");
  dump_int(OB_PROP_IR_BRIGHTNESS_INT, "ir_brightness");
  ofs.close();
  std::cout << "[OK] 参数已导出到 " << g_out_file << "\n";
}

// 查询 D2C 对齐支持的深度分辨率
static void listD2CProfiles(const std::shared_ptr<Pipeline> &pipeline,
                            const std::shared_ptr<Device> &device) {
  auto color_profile = findProfileWithFormat(device, OB_SENSOR_COLOR, 640, 480, OB_FORMAT_RGB);
  if (!color_profile) color_profile = findProfile(device, OB_SENSOR_COLOR, 640, 480);
  if (!color_profile) {
    std::cout << "[D2C] 无法获取彩色 profile\n";
    return;
  }
  for (auto mode : {ALIGN_D2C_SW_MODE, ALIGN_D2C_HW_MODE}) {
    std::cout << "[D2C] " << (mode == ALIGN_D2C_SW_MODE ? "软件对齐(SW)" : "硬件对齐(HW)")
              << " 支持彩色 " << color_profile->width() << "x" << color_profile->height()
              << " 的深度分辨率:\n";
    try {
      auto d2c_list = pipeline->getD2CDepthProfileList(color_profile, mode);
      if (!d2c_list || d2c_list->count() == 0) {
        std::cout << "    无\n";
        continue;
      }
      for (size_t i = 0; i < d2c_list->count(); i++) {
        auto p = d2c_list->getProfile(i)->as<VideoStreamProfile>();
        std::cout << "    " << p->width() << "x" << p->height() << " @ " << p->fps()
                  << "fps  " << magic_enum::enum_name(p->format()) << "\n";
      }
    } catch (const std::exception &e) {
      std::cout << "    查询失败: " << e.what() << "\n";
    }
  }
}

// 测试深度-彩色软件对齐是否可用
static void alignTest(const std::shared_ptr<Device> &device) {
  auto pipeline = std::make_shared<Pipeline>(device);
  auto config = std::make_shared<Config>();
  auto depth_profile = findProfile(device, OB_SENSOR_DEPTH, 640, 480);
  auto color_profile = findProfileWithFormat(device, OB_SENSOR_COLOR, 640, 480, OB_FORMAT_RGB);
  if (!depth_profile || !color_profile) {
    std::cout << "[ALIGN] 无法获取 depth/color profile\n";
    return;
  }
  config->enableStream(depth_profile);
  config->enableStream(color_profile);
  config->setAlignMode(ALIGN_D2C_SW_MODE);
  config->setDepthScaleRequire(true);
  try {
    pipeline->start(config);
  } catch (const std::exception &e) {
    std::cout << "[ALIGN] 启动失败: " << e.what() << "\n";
    return;
  }
  std::cout << "[ALIGN] 已启动 SW 对齐，等待帧...\n";
  for (int i = 0; i < 10; i++) {
    auto fs = pipeline->waitForFrames(3000);
    if (!fs) continue;
    auto depth = fs->getFrame(OB_FRAME_DEPTH);
    auto color = fs->getFrame(OB_FRAME_COLOR);
    if (depth && color) {
      auto dv = depth->as<VideoFrame>();
      auto cv = color->as<VideoFrame>();
      std::cout << "[ALIGN] 第" << i << "帧 OK: depth " << dv->width() << "x"
                << dv->height() << " color " << cv->width() << "x" << cv->height() << "\n";
    }
  }
  pipeline->stop();
}

// 打印相机内参/外参
static void printCameraParam(const std::shared_ptr<Pipeline> &pipeline) {
  try {
    auto cp = pipeline->getCameraParam();
    std::cout << "[PARAM] rgb  : " << cp.rgbIntrinsic.width << "x" << cp.rgbIntrinsic.height
              << " fx=" << cp.rgbIntrinsic.fx << " fy=" << cp.rgbIntrinsic.fy
              << " cx=" << cp.rgbIntrinsic.cx << " cy=" << cp.rgbIntrinsic.cy << "\n";
    std::cout << "[PARAM] depth: " << cp.depthIntrinsic.width << "x" << cp.depthIntrinsic.height
              << " fx=" << cp.depthIntrinsic.fx << " fy=" << cp.depthIntrinsic.fy
              << " cx=" << cp.depthIntrinsic.cx << " cy=" << cp.depthIntrinsic.cy << "\n";
    std::cout << "[PARAM] depth->color 外参 trans(mm): " << cp.transform.trans[0] << ", "
              << cp.transform.trans[1] << ", " << cp.transform.trans[2] << "\n";
    std::cout << "[PARAM] rot: " << cp.transform.rot[0] << " " << cp.transform.rot[1] << " "
              << cp.transform.rot[2] << " " << cp.transform.rot[3] << " " << cp.transform.rot[4]
              << " " << cp.transform.rot[5] << " " << cp.transform.rot[6] << " "
              << cp.transform.rot[7] << " " << cp.transform.rot[8] << "\n";
  } catch (const std::exception &e) {
    std::cout << "[PARAM] 获取失败: " << e.what() << "\n";
  }
}

int main(int argc, char **argv) {
  for (int i = 1; i < argc; i++) {
    std::string arg = argv[i];
    if (arg == "--list") {
      g_list_only = true;
    } else if (arg == "--d2c-list") {
      g_d2c_list = true;
    } else if (arg == "--align-test") {
      g_align_test = true;
    } else if (arg == "--cam-param") {
      g_cam_param = true;
    } else if (arg == "--set" && i + 1 < argc) {
      std::string kv = argv[++i];
      auto pos = kv.find('=');
      if (pos == std::string::npos) {
        std::cout << "[错误] --set 需要 key=value 形式\n";
        return 1;
      }
      g_sets.emplace_back(kv.substr(0, pos), kv.substr(pos + 1));
    } else if (arg == "--depth-mode" && i + 1 < argc) {
      g_depth_mode = argv[++i];
    } else if (arg == "--capture" && i + 1 < argc) {
      g_capture_dir = argv[++i];
    } else if (arg == "--out" && i + 1 < argc) {
      g_out_file = argv[++i];
    } else if (arg == "-h" || arg == "--help") {
      printUsage(argv[0]);
      return 0;
    } else {
      std::cout << "[错误] 未知参数: " << arg << "\n";
      printUsage(argv[0]);
      return 1;
    }
  }

  try {
    auto pipeline = std::make_shared<Pipeline>();
    auto device = pipeline->getDevice();
    if (!device) {
      std::cout << "未找到设备！请确认:\n"
                << "  1. 相机 USB 已连接\n"
                << "  2. 相机节点已停止（设备需独占访问）\n";
      return 1;
    }
    printDeviceInfo(device);

    if (g_d2c_list) {
      listD2CProfiles(pipeline, device);
      return 0;
    }
    if (g_align_test) {
      alignTest(device);
      return 0;
    }
    if (g_cam_param) {
      printCameraParam(pipeline);
      return 0;
    }

    applyDepthMode(device);
    applySets(device);

    if (g_list_only) {
      listProfiles(device);
      listDepthModes(device);
      printKeyProperties(device);
    } else {
      listProfiles(device);
      listDepthModes(device);
      printKeyProperties(device);
    }

    captureFrames(device);
    exportYaml(device);

    std::cout << "\n提示: 对比不同参数组合保存的 depth_colored.png 效果，"
              << "把最合适的参数填入 astra_pro_plus.launch.py。\n";
  } catch (const std::exception &e) {
    std::cout << "[错误] " << e.what() << "\n";
    std::cout << "如果提示设备已被占用，请先停止正在运行的相机节点。\n";
    return 1;
  }
  return 0;
}
