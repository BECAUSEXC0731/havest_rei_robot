-- ============================================================
-- Fox 2D SLAM 配置（Cartographer）
-- 适配：ydlidar 2D 激光(/scan) + 底盘里程计(/odom)，无 IMU
-- 坐标系：map -> odom(底盘驱动发布) -> base_footprint -> front_lidar_link
-- ============================================================

include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,

  map_frame = "map",
  tracking_frame = "base_footprint",
  published_frame = "odom",          -- Cartographer 发布 map -> odom
  odom_frame = "odom",
  provide_odom_frame = false,        -- 底盘驱动已发布 odom -> base_footprint TF
  publish_frame_projected_to_2d = false,

  use_pose_extrapolator = true,
  use_odometry = true,               -- 使用 /odom 里程计做运动预测
  use_nav_sat = false,
  use_landmarks = false,

  num_laser_scans = 1,               -- /scan 2D LaserScan
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,

  lookup_transform_timeout_sec = 0.2,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,

  rangefinder_sampling_ratio = 1.,
  odometry_sampling_ratio = 1.,
  fixed_frame_pose_sampling_ratio = 1.,
  imu_sampling_ratio = 1.,
  landmarks_sampling_ratio = 1.,
}

MAP_BUILDER.use_trajectory_builder_2d = true
MAP_BUILDER.num_background_threads = 4

-- ── 2D 轨迹构建器（前端：扫描匹配 + 子图） ──
TRAJECTORY_BUILDER_2D.use_imu_data = false
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true
TRAJECTORY_BUILDER_2D.min_range = 0.1          -- 与雷达 range_min 一致
TRAJECTORY_BUILDER_2D.max_range = 6.0          -- 与雷达 range_max 一致
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 5.0
TRAJECTORY_BUILDER_2D.num_accumulated_range_data = 1

-- 子图
TRAJECTORY_BUILDER_2D.submaps.grid_options_2d.resolution = 0.05
TRAJECTORY_BUILDER_2D.submaps.num_range_data = 60

-- 扫描匹配
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.linear_search_window = 0.1
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.translation_delta_cost_weight = 10.
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.rotation_delta_cost_weight = 1e-1
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 1.
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 1.

-- 运动滤波：降低无效帧插入
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = 0.03
TRAJECTORY_BUILDER_2D.motion_filter.max_distance_meters = 0.05
TRAJECTORY_BUILDER_2D.motion_filter.max_time_seconds = 0.5

-- ── 位姿图（后端：回环检测 + 全局优化） ──
POSE_GRAPH.optimize_every_n_nodes = 90
POSE_GRAPH.constraint_builder.min_score = 0.65
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.6
POSE_GRAPH.constraint_builder.loop_closure_translation_weight = 1.1e4
POSE_GRAPH.constraint_builder.loop_closure_rotation_weight = 1e5
POSE_GRAPH.constraint_builder.log_matches = false

POSE_GRAPH.optimization_problem.huber_scale = 1e2
POSE_GRAPH.optimization_problem.local_slam_pose_translation_weight = 1e5
POSE_GRAPH.optimization_problem.local_slam_pose_rotation_weight = 1e8
POSE_GRAPH.optimization_problem.odometry_translation_weight = 1e5
POSE_GRAPH.optimization_problem.odometry_rotation_weight = 1e5

return options
