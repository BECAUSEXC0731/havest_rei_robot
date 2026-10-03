cmake_minimum_required(VERSION 3.8)
project(arm_controller)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -std=c++17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# ── Messages ──
set(msg_files
  "msg/Control.msg"
)

# ── Services ──
set(srv_files
  "srv/Number.srv"
  "srv/PickPlace.srv"
  "srv/Move.srv"
  "srv/RelativePos.srv"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  DEPENDENCIES std_msgs geometry_msgs builtin_interfaces
)

rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")

# ── Include ──
include_directories(
  include
)

# ── arm_swiftpro ──
add_executable(arm_swiftpro
  src/arm_swiftpro.cpp
)
ament_target_dependencies(arm_swiftpro
  rclcpp
  std_msgs
  geometry_msgs
  sensor_msgs
  std_srvs
)
target_link_libraries(arm_swiftpro
  "${cpp_typesupport_target}"
)

# ── pick_ar ──
add_executable(pick_ar
  src/pick_ar.cpp
)
ament_target_dependencies(pick_ar
  rclcpp
  std_msgs
  geometry_msgs
  sensor_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
  std_srvs
)
target_link_libraries(pick_ar
  "${cpp_typesupport_target}"
)

# ── Install ──
install(TARGETS
  arm_swiftpro
  pick_ar
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/explore_workspace.py
  scripts/gen_marker.py
  scripts/hand_eye_calib.py
  scripts/grab_test.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()