#include <rclcpp/rclcpp.hpp>
#include <rei_robot_base/rei_robot_base.h>

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<reinovo_base::ReiBaseRos>();
  if (!node->Init()) {
    RCLCPP_ERROR(rclcpp::get_logger("rei_robot_base_ros2"), "初始化失败");
    return -1;
  }
  node->Run();
  rclcpp::shutdown();
  return 0;
}
