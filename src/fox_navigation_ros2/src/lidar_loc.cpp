// ============================================================================
// lidar_loc — 激光雷达"势场爬山匹配"定位节点 (ROS2 / Nav2 版)
// ----------------------------------------------------------------------------
// 算法来源: src/jie_ware/src/lidar_loc.cpp (ROS1, 阿杰/6-robot) 的等价移植
//   B站《一种简单易用的激光雷达定位方法》: BV1fB29YzEgP
//
// 用途: 替代 nav2_amcl。只做一件事——发布 map→odom TF(Nav2 的全局/局部
//   代价地图、planner/controller 都只依赖这条 TF),不依赖里程计预测。
//
// 原理(与原版逐行等价, 不依赖 OpenCV, 势场用纯 C++ 实现):
//   1) 订阅 /map: 裁切到有效区域(障碍包围盒外扩 50 格), 对每个障碍点
//      (值==100) 在 ±50 栅格邻域按 "离墙越近越亮" 线性扩散成势场图
//      map_temp(255*max(0, 1 - d/50)), 作为匹配打分图。
//   2) 订阅 /scan: 每帧把有效激光点经 TF(base←laser)转到 base 系并换算成
//      栅格坐标; 在当前估计位姿 (lidar_x,lidar_y,lidar_yaw) 下把点云投影到
//      map_temp 求和作为匹配分。
//   3) 爬山: 在 5 个位移(0,±1格) × 3 个角度(0,±1°) 共 15 种候选里取
//      分数最高者逐步更新位姿, 迭代至收敛(连续 10 次变化 <5 格 且 <5°)。
//   4) T_map_odom = T_map_base * (T_odom_base)^-1, 30Hz 广播 map→odom TF。
//
// ⚠️ 与 AMCL 相同的使用前提:
//   - 机器人上电后需在 RViz 用 "2D Pose Estimate" 给一次初始位姿(/initialpose),
//     或默认从地图世界原点 (0,0,0) 起步;
//   - 算法每帧只在上一次位姿的 ±1 格/±1° 邻域搜索, 空旷区无梯度时位姿冻结,
//     必须靠近墙/障碍才有匹配约束(沿墙行走时表现最佳);
//   - 它是确定性匹配(无随机粒子), 一旦初始给错且当前环境无墙特征会定不住。
//     这与 AMCL 的行为不同, 属算法固有特性, 需实测验证。
// ============================================================================

#include <atomic>
#include <cmath>
#include <deque>
#include <mutex>
#include <string>
#include <thread>
#include <tuple>
#include <vector>

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/occupancy_grid.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/transform_listener.h>

using std::placeholders::_1;

namespace
{
constexpr double kDegToRad = M_PI / 180.0;
}

class LidarLoc : public rclcpp::Node
{
public:
  LidarLoc()
  : Node("lidar_loc")
  {
    // ---------- 参数(与原版同名, 值按 fox 机器人默认) ----------
    base_frame_ = this->declare_parameter<std::string>("base_frame", "base_footprint");
    odom_frame_ = this->declare_parameter<std::string>("odom_frame", "odom");
    laser_frame_ = this->declare_parameter<std::string>("laser_frame", "front_lidar_link");
    laser_topic_ = this->declare_parameter<std::string>("laser_topic", "/scan");

    // ---------- 订阅 ----------
    map_sub_ = this->create_subscription<nav_msgs::msg::OccupancyGrid>(
      "map", rclcpp::QoS(1).transient_local(),
      std::bind(&LidarLoc::mapCallback, this, _1));
    scan_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      laser_topic_, rclcpp::QoS(1).best_effort(),
      std::bind(&LidarLoc::scanCallback, this, _1));
    initial_pose_sub_ = this->create_subscription<geometry_msgs::msg::PoseWithCovarianceStamped>(
      "initialpose", rclcpp::QoS(1),
      std::bind(&LidarLoc::initialPoseCallback, this, _1));

    // ---------- 发布 ----------
    pose_pub_ = this->create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>(
      "lidar_loc_pose", rclcpp::QoS(10));

    // TF listener 绑定本节点 executor(spin 时持续消费 /tf), 不开内部线程,
    // 保证与 laser/map 回调同一执行上下文, 由 worker 线程只读查询 buffer
    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_, this, false);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

    // 独立工作线程: 统一做 地图裁切/建场 → 激光匹配 → 30Hz TF 广播
    worker_ = std::thread(&LidarLoc::workerLoop, this);
    RCLCPP_INFO(this->get_logger(),
      "lidar_loc 已启动: base=%s odom=%s laser_frame=%s laser_topic=%s",
      base_frame_.c_str(), odom_frame_.c_str(), laser_frame_.c_str(), laser_topic_.c_str());
  }

  ~LidarLoc()
  {
    stop_ = true;
    if (worker_.joinable()) {
      worker_.join();
    }
  }

private:
  // ============================ 回调(只做轻量拷贝) ============================

  // 原版 mapCallback: 存地图; 裁切/建场较重, 放到 worker 线程做
  void mapCallback(const nav_msgs::msg::OccupancyGrid::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lk(map_mutex_);
    pending_map_.width = msg->info.width;
    pending_map_.height = msg->info.height;
    pending_map_.resolution = msg->info.resolution;
    pending_map_.origin_x = msg->info.origin.position.x;
    pending_map_.origin_y = msg->info.origin.position.y;
    pending_map_.data.assign(msg->data.begin(), msg->data.end());
    map_pending_ = true;
    RCLCPP_INFO(this->get_logger(),
      "收到地图 %dx%d res=%.3f origin=(%.2f,%.2f)",
      pending_map_.width, pending_map_.height, pending_map_.resolution,
      pending_map_.origin_x, pending_map_.origin_y);
  }

  // 原版 scanCallback 的取数部分: 拷贝最新一帧 scan
  void scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lk(scan_mutex_);
    scan_ranges_.assign(msg->ranges.begin(), msg->ranges.end());
    scan_angle_min_ = msg->angle_min;
    scan_angle_increment_ = msg->angle_increment;
    scan_range_min_ = msg->range_min;
    scan_range_max_ = msg->range_max;
    scan_pending_ = true;
  }

  // 原版 initialPoseCallback: 把 initialpose 缓存, 由 worker 在有地图后应用
  void initialPoseCallback(const geometry_msgs::msg::PoseWithCovarianceStamped::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lk(initial_mutex_);
    pending_initial_ = *msg;
    initial_pending_ = true;
    RCLCPP_INFO(this->get_logger(), "收到初始位姿, 将应用到定位");
  }

  // ============================ worker 主循环 ============================
  void workerLoop()
  {
    rclcpp::Rate rate(30.0);  // 与原版主循环 30Hz 一致
    while (rclcpp::ok() && !stop_) {
      // 1. 有地图待处理: 裁切 + 建势场。仅在用户从未给过 initialpose 时才兜底
      //    初始化为世界原点 (0,0,0), 避免覆盖用户刚设好的位姿
      if (consumePendingMap()) {
        cropMap();
        processMap();
        if (!initial_applied_) {
          resetToPose(0.0, 0.0, 0.0);
        }
        got_map_ = true;
      }

      // 2. 有待应用的 initialpose
      if (initial_pending_ && got_map_) {
        applyPendingInitialPose();
      }

      // 3. 有新 scan 且地图就绪 → 匹配(爬山)
      if (scan_pending_ && got_map_) {
        std::vector<float> ranges;
        double angle_min, angle_inc, range_min, range_max;
        {
          std::lock_guard<std::mutex> lk(scan_mutex_);
          ranges = scan_ranges_;
          angle_min = scan_angle_min_;
          angle_inc = scan_angle_increment_;
          range_min = scan_range_min_;
          range_max = scan_range_max_;
          scan_pending_ = false;
        }
        doMatch(ranges, angle_min, angle_inc, range_min, range_max);
        got_scan_ = true;
      }

      // 4. 广播 map→odom TF(有 scan 且有地图才发, 与原版 pose_tf 一致)
      if (got_scan_ && got_map_) {
        publishMapToOdomTf();
      }

      rate.sleep();
    }
  }

  // ============================ 地图裁切 ============================
  void cropMap()
  {
    // 取地图消息的深拷贝(consumePendingMap 已存到本地 map_)
    const int width = map_.width;
    const int height = map_.height;
    if (width <= 0 || height <= 0 || map_.resolution <= 0.0) {
      return;
    }

    // 原版: cv::Mat map_raw(h,w) 初始 128(gray); 填充 data(uchar 截断)
    //   ROS1 OccupancyGrid.data 为 int8; unknown(-1) 经 uchar 截断为 255,
    //   但后续只统计 ==100 与建场只扫 ==100, 因此 -1 的处理不影响算法。
    std::vector<uint8_t> map_raw(static_cast<size_t>(width) * height, 128);
    for (int y = 0; y < height; ++y) {
      for (int x = 0; x < width; ++x) {
        int v = map_.data[static_cast<size_t>(y) * width + x];
        map_raw[static_cast<size_t>(y) * width + x] = static_cast<uint8_t>(v);
      }
    }

    // 统计障碍(==100)包围盒
    int xMax = width / 2, xMin = width / 2;
    int yMax = height / 2, yMin = height / 2;
    bool bFirstPoint = true;
    for (int y = 0; y < height; ++y) {
      for (int x = 0; x < width; ++x) {
        if (map_.data[static_cast<size_t>(y) * width + x] == 100) {
          if (bFirstPoint) {
            xMax = xMin = x;
            yMax = yMin = y;
            bFirstPoint = false;
            continue;
          }
          xMin = std::min(xMin, x);
          xMax = std::max(xMax, x);
          yMin = std::min(yMin, y);
          yMax = std::max(yMax, y);
        }
      }
    }

    // 按有效区域外扩 50 格裁剪
    int cen_x = (xMin + xMax) / 2;
    int cen_y = (yMin + yMax) / 2;
    int new_half_width = std::abs(xMax - xMin) / 2 + 50;
    int new_half_height = std::abs(yMax - yMin) / 2 + 50;
    int new_origin_x = cen_x - new_half_width;
    int new_origin_y = cen_y - new_half_height;
    int new_width = new_half_width * 2;
    int new_height = new_half_height * 2;
    if (new_origin_x < 0) { new_origin_x = 0; }
    if ((new_origin_x + new_width) > width) { new_width = width - new_origin_x; }
    if (new_origin_y < 0) { new_origin_y = 0; }
    if ((new_origin_y + new_height) > height) { new_height = height - new_origin_y; }

    // roi = map_raw(new_origin_x, new_origin_y, new_width, new_height).clone()
    roi_x_ = new_origin_x;
    roi_y_ = new_origin_y;
    crop_w_ = new_width;
    crop_h_ = new_height;
    map_cropped_.assign(static_cast<size_t>(crop_w_) * crop_h_, 0);
    for (int y = 0; y < crop_h_; ++y) {
      for (int x = 0; x < crop_w_; ++x) {
        map_cropped_[static_cast<size_t>(y) * crop_w_ + x] =
          map_raw[static_cast<size_t>(y + roi_y_) * width + (x + roi_x_)];
      }
    }

    RCLCPP_INFO(this->get_logger(),
      "地图裁切: crop %dx%d @ roi(%d,%d) / full %dx%d",
      crop_w_, crop_h_, roi_x_, roi_y_, width, height);
  }

  // ============================ 建势场图(等价 processMap) ============================
  // 预计算 101x101 渐变掩模: 距中心 d 格的值 = 255*max(0, 1 - d/50)
  void processMap()
  {
    if (crop_w_ <= 0 || crop_h_ <= 0) { return; }
    map_temp_.assign(static_cast<size_t>(crop_w_) * crop_h_, 0);

    const int mask_size = 101;
    const int center = mask_size / 2;  // 50
    std::vector<int> gradient(mask_size * mask_size, 0);
    for (int my = 0; my < mask_size; ++my) {
      for (int mx = 0; mx < mask_size; ++mx) {
        double d = std::hypot(static_cast<double>(mx - center),
                              static_cast<double>(my - center));
        gradient[static_cast<size_t>(my) * mask_size + mx] =
          static_cast<int>(255.0 * std::max(0.0, 1.0 - d / static_cast<double>(center)));
      }
    }

    // 对每个障碍点在其 ±50 邻域做 elementwise max(等价 cv::max(region, mask))
    for (int y = 0; y < crop_h_; ++y) {
      for (int x = 0; x < crop_w_; ++x) {
        if (map_cropped_[static_cast<size_t>(y) * crop_w_ + x] != 100) {
          continue;
        }
        const int left = std::max(0, x - center);
        const int top = std::max(0, y - center);
        const int right = std::min(crop_w_ - 1, x + center);
        const int bottom = std::min(crop_h_ - 1, y + center);
        for (int yy = top; yy <= bottom; ++yy) {
          for (int xx = left; xx <= right; ++xx) {
            const int dx = xx - x;
            const int dy = yy - y;
            const int mask_val = gradient[static_cast<size_t>(dy + center) * mask_size + (dx + center)];
            auto & cell = map_temp_[static_cast<size_t>(yy) * crop_w_ + xx];
            if (mask_val > cell) { cell = mask_val; }
          }
        }
      }
    }
    RCLCPP_INFO(this->get_logger(), "势场图已重建 (%d x %d)", crop_w_, crop_h_);
  }

  // ============================ 激光匹配(等价 scanCallback 主循环) ============================
  void doMatch(
    const std::vector<float> & ranges,
    double angle_min, double angle_inc,
    double range_min, double range_max)
  {
    if (map_temp_.empty()) { return; }

    // 1. 查 base←laser TF(把激光点转到 base 系)
    geometry_msgs::msg::TransformStamped t;
    try {
      t = tf_buffer_->lookupTransform(
        base_frame_, laser_frame_, tf2::TimePointZero);
    } catch (const tf2::TransformException & e) {
      RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "%s", e.what());
      return;
    }
    tf2::Quaternion q_laser;
    tf2::fromMsg(t.transform.rotation, q_laser);
    double roll, pitch, laser_yaw;
    tf2::Matrix3x3(q_laser).getRPY(roll, pitch, laser_yaw);
    const double cos_yaw = std::cos(laser_yaw), sin_yaw = std::sin(laser_yaw);
    const double tx = t.transform.translation.x;
    const double ty = t.transform.translation.y;

    const double res = map_.resolution;

    // 2. 有效点 → base 系 → 栅格坐标(相对 base)
    std::vector<std::pair<double, double>> scan_points;  // (x,y) 单位: 栅格
    double angle = angle_min;
    for (size_t i = 0; i < ranges.size(); ++i) {
      const float r = ranges[i];
      if (r >= range_min && r <= range_max) {
        // 标准 LaserScan 几何(与 AMCL/costmap 一致): 0°=x前向, 角逆时针为正, y向左为正
        const double x_laser = r * std::cos(angle);
        const double y_laser = r * std::sin(angle);
        // 2D 旋转平移 (等价原版 tf2::doTransform point → base)
        const double x_base = cos_yaw * x_laser - sin_yaw * y_laser + tx;
        const double y_base = sin_yaw * x_laser + cos_yaw * y_laser + ty;
        scan_points.emplace_back(x_base / res, y_base / res);
      }
      angle += angle_inc;
    }
    if (scan_points.empty()) { return; }

    // 注: lidar_x_/lidar_y_/lidar_yaw_/data_queue_ 仅由 worker 线程读写
    // (doMatch/applyPendingInitialPose/resetToPose 均串行在 workerLoop), 无需锁
    float & lx = lidar_x_;
    float & ly = lidar_y_;
    float & lyaw = lidar_yaw_;

    // 3. 爬山匹配: 5 位移 × 3 角度, 取分数最大者, 迭代至收敛
    //    安全上限: 与 check() 组合保证正常必收敛(空旷区全 0 时 10 次即停)
    int max_iter = 500;
    while (rclcpp::ok() && !stop_ && (max_iter-- > 0)) {
      std::vector<std::pair<double, double>> transform_points, clockwise_points, counter_points;
      transform_points.reserve(scan_points.size());
      clockwise_points.reserve(scan_points.size());
      counter_points.reserve(scan_points.size());

      const double yaw_origin = lyaw;
      // 三种候选航向: 0, +1°, -1°(lidar_yaw 为世界航向, 逆时针为正)
      for (size_t k = 0; k < 3; ++k) {
        const double eff_yaw = yaw_origin + (k == 1 ? kDegToRad : (k == 2 ? -kDegToRad : 0.0));
        const double c = std::cos(eff_yaw), s = std::sin(eff_yaw);
        auto & out = (k == 0 ? transform_points : (k == 1 ? clockwise_points : counter_points));
        for (const auto & p : scan_points) {
          // 标准布局(与 AMCL 一致): 地图栅格 (col=lidar_x+rx, row=lidar_y+ry),
          // row 向下增大 = 世界 +Y(行向上), lidar_y 即地图行号
          const double rx = p.first * c - p.second * s;
          const double ry = p.first * s + p.second * c;
          out.emplace_back(rx + lx, ry + ly);
        }
      }
      const std::vector<std::vector<std::pair<double, double>>*> point_sets = {
        &transform_points, &clockwise_points, &counter_points};
      // 5 个位移候选(原版 offsets 顺序)
      const std::vector<std::pair<double, double>> offsets = {
        {0, 0}, {1, 0}, {-1, 0}, {0, 1}, {0, -1}};
      const double yaw_offsets[3] = {0.0, kDegToRad, -kDegToRad};

      int max_sum = 0;
      double best_dx = 0, best_dy = 0, best_dyaw = 0;
      for (size_t i = 0; i < offsets.size(); ++i) {
        for (size_t j = 0; j < point_sets.size(); ++j) {
          int sum = 0;
          for (const auto & p : *point_sets[j]) {
            // 原版: float px/py 直接作为 cv::Mat 索引 → 隐式向零截断
            const int ix = static_cast<int>(p.first + offsets[i].first);
            const int iy = static_cast<int>(p.second + offsets[i].second);
            if (ix >= 0 && ix < crop_w_ && iy >= 0 && iy < crop_h_) {
              sum += map_temp_[static_cast<size_t>(iy) * crop_w_ + ix];
            }
          }
          if (sum > max_sum) {
            max_sum = sum;
            best_dx = offsets[i].first;
            best_dy = offsets[i].second;
            best_dyaw = yaw_offsets[j];
          }
        }
      }
      lx += best_dx;
      ly += best_dy;
      lyaw += best_dyaw;

      // 4. 收敛判断(等价原版 check())
      if (checkConverged(lx, ly, lyaw)) {
        break;
      }
    }
  }

  // 原版 check(): 连续 max_size(10) 次位姿记录首尾差 <5 格 且 <5° → 收敛
  bool checkConverged(float x, float y, float yaw)
  {
    constexpr size_t max_size = 10;
    if (x == 0.0f && y == 0.0f && yaw == 0.0f) {
      data_queue_.clear();
      return true;
    }
    data_queue_.emplace_back(x, y, yaw);
    if (data_queue_.size() > max_size) {
      data_queue_.pop_front();
    }
    if (data_queue_.size() == max_size) {
      const auto & first = data_queue_.front();
      const auto & last = data_queue_.back();
      const float dx = std::abs(std::get<0>(last) - std::get<0>(first));
      const float dy = std::abs(std::get<1>(last) - std::get<1>(first));
      const float dyaw = std::abs(std::get<2>(last) - std::get<2>(first));
      if (dx < 5.0f && dy < 5.0f && dyaw < 5.0 * kDegToRad) {
        data_queue_.clear();
        return true;
      }
    }
    return false;
  }

  // ============================ TF 广播(等价 pose_tf) ============================
  void publishMapToOdomTf()
  {
    // 1. 裁切栅格像素位姿 → 完整地图栅格 → map 系米制(原始匹配结果)
    const double full_pixel_x = lidar_x_ + roi_x_;
    const double full_pixel_y = lidar_y_ + roi_y_;
    const double res = map_.resolution;
    const double raw_x = full_pixel_x * res + map_.origin_x;
    const double raw_y = full_pixel_y * res + map_.origin_y;
    const double raw_yaw = lidar_yaw_;

    // 2. 查 odom→base(同时用于判断机器人是否真的在动)
    geometry_msgs::msg::TransformStamped odom_to_base;
    try {
      odom_to_base = tf_buffer_->lookupTransform(
        odom_frame_, base_frame_, tf2::TimePointZero);
    } catch (const tf2::TransformException & e) {
      RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "%s", e.what());
      return;
    }
    const double ox = odom_to_base.transform.translation.x;
    const double oy = odom_to_base.transform.translation.y;
    tf2::Quaternion oq;
    tf2::fromMsg(odom_to_base.transform.rotation, oq);
    double o_roll, o_pitch, o_yaw;
    tf2::Matrix3x3(oq).getRPY(o_roll, o_pitch, o_yaw);

    // 3. 平滑/锁存: 消除"静止时 lidar 匹配航向 ±1° 抖动"传导到 map→odom
    //    - odom 有位移(>1cm 或 >0.5°) = 真在动 → 直接用匹配结果(几乎无滞后)
    //    - odom 没动, 匹配结果只在小范围抖(≤8cm / ≤1.5°) = 匹配噪声 → 锁存上次值(冻结)
    //    - odom 没动但匹配认为明显变了(被打滑推走/抬走) → 仍跟随
    double out_x, out_y, out_yaw;
    if (!lock_valid_) {
      out_x = raw_x; out_y = raw_y; out_yaw = raw_yaw;
      lock_valid_ = true;
    } else {
      const double d_odom = std::hypot(ox - last_odom_x_, oy - last_odom_y_);
      const double d_odom_yaw = std::fabs(normAngDiff(o_yaw - last_odom_yaw_));
      const bool moved = d_odom > 0.01 || d_odom_yaw > 0.5 * kDegToRad;
      const bool small_jitter =
        std::fabs(raw_x - lock_x_) < 0.08 &&
        std::fabs(raw_y - lock_y_) < 0.08 &&
        std::fabs(normAngDiff(raw_yaw - lock_yaw_)) < 1.5 * kDegToRad;
      if (moved || !small_jitter) {
        out_x = raw_x; out_y = raw_y; out_yaw = raw_yaw;
      } else {
        out_x = lock_x_; out_y = lock_y_; out_yaw = lock_yaw_;  // 冻结
      }
    }
    lock_x_ = out_x; lock_y_ = out_y; lock_yaw_ = out_yaw;
    last_odom_x_ = ox; last_odom_y_ = oy; last_odom_yaw_ = o_yaw;

    // 4. T_map_odom = T_map_base * (T_odom_base)^-1
    //    T_map_base = Rot(out_yaw)*p + (out_x,out_y)
    //    T_odom_base = Rot(o_yaw)*p + t_odom
    //    复合: 旋转 m_yaw = out_yaw - o_yaw; 平移 m = t_map - R(m_yaw)*t_odom
    const double m_yaw = out_yaw - o_yaw;
    const double mc = std::cos(m_yaw), ms = std::sin(m_yaw);
    const double m_x = out_x - (mc * ox - ms * oy);
    const double m_y = out_y - (ms * ox + mc * oy);

    geometry_msgs::msg::TransformStamped msg;
    msg.header.stamp = this->now();
    msg.header.frame_id = "map";
    msg.child_frame_id = odom_frame_;
    msg.transform.translation.x = m_x;
    msg.transform.translation.y = m_y;
    msg.transform.translation.z = 0.0;
    tf2::Quaternion q;
    q.setRPY(0, 0, m_yaw);
    msg.transform.rotation = tf2::toMsg(q);
    tf_broadcaster_->sendTransform(msg);

    // 5. 顺带发布当前 map 系位姿(替代 /amcl_pose 供诊断脚本用)
    geometry_msgs::msg::PoseWithCovarianceStamped pose;
    pose.header.stamp = msg.header.stamp;
    pose.header.frame_id = "map";
    pose.pose.pose.position.x = out_x;
    pose.pose.pose.position.y = out_y;
    tf2::Quaternion pq;
    pq.setRPY(0, 0, out_yaw);
    pose.pose.pose.orientation = tf2::toMsg(pq);
    pose_pub_->publish(pose);
  }

  // 角度差归一化到 [-π, π)
  static double normAngDiff(double a)
  {
    while (a > M_PI) { a -= 2.0 * M_PI; }
    while (a < -M_PI) { a += 2.0 * M_PI; }
    return a;
  }

  // ============================ initialpose 应用 ============================
  void applyPendingInitialPose()
  {
    geometry_msgs::msg::PoseWithCovarianceStamped pending;
    {
      std::lock_guard<std::mutex> lk(initial_mutex_);
      if (!initial_pending_) { return; }
      initial_pending_ = false;
      pending = pending_initial_;
    }

    const auto & p = pending.pose.pose;
    const double map_x = p.position.x;
    const double map_y = p.position.y;
    tf2::Quaternion q;
    tf2::fromMsg(p.orientation, q);
    double roll, pitch, yaw;
    tf2::Matrix3x3(q).getRPY(roll, pitch, yaw);

    if (map_.resolution <= 0.0) { return; }
    lidar_x_ = static_cast<float>((map_x - map_.origin_x) / map_.resolution - roi_x_);
    lidar_y_ = static_cast<float>((map_y - map_.origin_y) / map_.resolution - roi_y_);
    lidar_yaw_ = static_cast<float>(yaw);   // 世界航向(逆时针为正)
    data_queue_.clear();
    initial_applied_ = true;
    RCLCPP_INFO(this->get_logger(),
      "初始位姿应用: map(%.2f, %.2f, %.1f°) → crop 栅格(%.1f, %.1f, %.1f°)",
      map_x, map_y, yaw * 180.0 / M_PI, lidar_x_, lidar_y_, lidar_yaw_ * 180.0 / M_PI);
  }

  // 等价 crop_map 里 initialPoseCallback(0,0,0); 仅 worker 线程调用
  void resetToPose(double map_x, double map_y, double yaw)
  {
    if (map_.resolution <= 0.0) { return; }
    lidar_x_ = static_cast<float>((map_x - map_.origin_x) / map_.resolution - roi_x_);
    lidar_y_ = static_cast<float>((map_y - map_.origin_y) / map_.resolution - roi_y_);
    lidar_yaw_ = static_cast<float>(yaw);   // AMCL 标准: 不取反
    data_queue_.clear();
    RCLCPP_INFO(this->get_logger(),
      "位姿重置为地图原点(%.2f,%.2f) → crop 栅格(%.1f, %.1f) (建议用 RViz 2D Pose Estimate 设初始位姿)",
      map_x, map_y, lidar_x_, lidar_y_);
  }

  // 从回调拷贝 pending map 到本地 map_
  bool consumePendingMap()
  {
    std::lock_guard<std::mutex> lk(map_mutex_);
    if (!map_pending_) { return false; }
    map_pending_ = false;
    map_.width = pending_map_.width;
    map_.height = pending_map_.height;
    map_.resolution = pending_map_.resolution;
    map_.origin_x = pending_map_.origin_x;
    map_.origin_y = pending_map_.origin_y;
    map_.data = pending_map_.data;
    return true;
  }

  // ============================ 成员 ============================
  std::string base_frame_;
  std::string odom_frame_;
  std::string laser_frame_;
  std::string laser_topic_;

  // 地图(worker 本地)
  struct MapData {
    int width = 0, height = 0;
    double resolution = 0.0;
    double origin_x = 0.0, origin_y = 0.0;
    std::vector<int8_t> data;
  } map_;
  int roi_x_ = 0, roi_y_ = 0, crop_w_ = 0, crop_h_ = 0;
  std::vector<uint8_t> map_cropped_;
  std::vector<int> map_temp_;
  bool got_map_ = false;

  // pending map(回调写入)
  std::mutex map_mutex_;
  MapData pending_map_;
  bool map_pending_ = false;

  // scan(回调写入)
  std::mutex scan_mutex_;
  std::vector<float> scan_ranges_;
  double scan_angle_min_ = 0, scan_angle_increment_ = 0;
  double scan_range_min_ = 0, scan_range_max_ = 0;
  bool scan_pending_ = false;
  bool got_scan_ = false;

  // pose(仅 worker 线程访问; initial 缓存由回调与 worker 共享, 用 initial_mutex_)
  float lidar_x_ = 250.0f, lidar_y_ = 250.0f, lidar_yaw_ = 0.0f;
  std::deque<std::tuple<float, float, float>> data_queue_;
  std::mutex initial_mutex_;
  geometry_msgs::msg::PoseWithCovarianceStamped pending_initial_;
  bool initial_pending_ = false;
  bool initial_applied_ = false;   // 用户是否已给过初始位姿(避免地图到达时覆盖)
  // 输出锁存/平滑(消除静止时航向 ±1° 抖动传导到 map→odom; 见 publishMapToOdomTf)
  bool lock_valid_ = false;
  double lock_x_ = 0.0, lock_y_ = 0.0, lock_yaw_ = 0.0;
  double last_odom_x_ = 0.0, last_odom_y_ = 0.0, last_odom_yaw_ = 0.0;

  // ROS 接口
  rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr map_sub_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
  rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr initial_pose_sub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr pose_pub_;
  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

  std::thread worker_;
  std::atomic<bool> stop_{false};
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<LidarLoc>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  node.reset();  // 触发析构, join worker
  return 0;
}
