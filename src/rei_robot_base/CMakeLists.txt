cmake_minimum_required(VERSION 3.8)
project(rei_robot_base)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -std=c++17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(std_srvs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# ── Messages ──
set(msg_files
  "msg/CarData.msg"
  "msg/MotorCmd.msg"
  "msg/BumperCliff.msg"
)

# ── Services ──
set(srv_files
  "srv/SetIO.srv"
  "srv/Int8.srv"
  "srv/CtrlMode.srv"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  DEPENDENCIES std_msgs geometry_msgs builtin_interfaces
)

# ── Include ──
include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
)

# ── Kinematics lib ──
add_library(rei_kinematics
  src/kinematics/diff_kinematics.cpp
  src/kinematics/three_omni_kinematics.cpp
  src/kinematics/mecanum_box_kinematics.cpp
)
target_link_libraries(rei_kinematics Eigen3::Eigen)
ament_target_dependencies(rei_kinematics rclcpp)

# ── Communication lib ──
add_library(rei_base_communication
  src/communication/rei_base_communication.cpp
)
target_link_libraries(rei_base_communication modbus)
ament_target_dependencies(rei_base_communication rclcpp)

# ── Main executable ──
add_executable(robot_base_node
  src/rei_robot_base.cpp
  src/ros_node.cpp
)
ament_target_dependencies(robot_base_node
  rclcpp
  std_msgs
  std_srvs
  geometry_msgs
  nav_msgs
  sensor_msgs
  tf2
  tf2_ros
)
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(robot_base_node
  rei_kinematics
  rei_base_communication
  "${cpp_typesupport_target}"
)

# ── Install targets ──
install(TARGETS
  robot_base_node
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS
  rei_kinematics
  rei_base_communication
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

# ── Python scripts ──
# Python 版底盘驱动已废弃（行为与 C++ 版不一致，且会打断导航指令），
# 统一使用 C++ 版 robot_base_node（经 base.launch.py 启动），不再安装。
# install(PROGRAMS
#   scripts/fox_base_driver.py
#   DESTINATION lib/${PROJECT_NAME}
# )

install(DIRECTORY
  config
  launch
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION include/${PROJECT_NAME}
  FILES_MATCHING PATTERN "*.h"
  PATTERN ".svn" EXCLUDE
)

if(AMENT_ENABLE_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
