cmake_minimum_required(VERSION 3.8)
project(fox_navigation_ros2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -std=c++17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# lidar_loc: 激光雷达"势场爬山匹配"定位节点(替代 nav2_amcl)
# 算法移植自 src/jie_ware/src/lidar_loc.cpp (ROS1) → 发布 map→odom TF
add_executable(lidar_loc src/lidar_loc.cpp)
target_compile_features(lidar_loc PUBLIC cxx_std_17)
ament_target_dependencies(lidar_loc
  rclcpp
  tf2
  tf2_ros
  tf2_geometry_msgs
  nav_msgs
  sensor_msgs
  geometry_msgs
)
install(TARGETS lidar_loc
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  param
  rviz
  DESTINATION share/${PROJECT_NAME}
)

if(AMENT_ENABLE_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
