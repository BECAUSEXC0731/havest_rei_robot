cmake_minimum_required(VERSION 3.8)
project(fox_description_ros2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -std=c++17)
endif()

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  xacro
  meshes
  rviz
  DESTINATION share/${PROJECT_NAME}
)

if(AMENT_ENABLE_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
