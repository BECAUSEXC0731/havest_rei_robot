cmake_minimum_required(VERSION 3.8)
project(gripper_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# Python 节点安装
install(PROGRAMS
  scripts/gripper_node.py
  scripts/gripper_integration.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

# 确保可执行权限
set(PYTHON_SCRIPTS
  ${CMAKE_CURRENT_SOURCE_DIR}/scripts/gripper_node.py
  ${CMAKE_CURRENT_SOURCE_DIR}/scripts/gripper_integration.py
)
foreach(script ${PYTHON_SCRIPTS})
  file(CHMOD ${script} PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
       GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
endforeach()

ament_package()
