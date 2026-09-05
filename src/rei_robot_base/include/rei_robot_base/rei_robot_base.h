#pragma once

#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <sensor_msgs/msg/range.hpp>
#include <std_srvs/srv/empty.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <tf2_ros/transform_broadcaster.h>

#include <rei_robot_base/msg/car_data.hpp>
#include <rei_robot_base/msg/motor_cmd.hpp>
#include <rei_robot_base/msg/bumper_cliff.hpp>
#include <rei_robot_base/srv/set_io.hpp>
#include <rei_robot_base/srv/int8.hpp>

#include "communication/rei_base_communication.h"
#include "kinematics/kinematics_factory.h"

namespace reinovo_base {

class ReiBaseRos : public rclcpp::Node {
 public:
  ReiBaseRos();
  bool Init();
  int8_t ConnectBase();
  void Run();

 private:
  std::shared_ptr<BaseKin> kinematics_ptr_;

  // Services
  rclcpp::Service<rei_robot_base::srv::SetIO>::SharedPtr set_io_server_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr set_relay_server_;
  rclcpp::Service<rei_robot_base::srv::Int8>::SharedPtr extra_motor_server_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr set_buzzer_server_;
  rclcpp::Service<std_srvs::srv::Empty>::SharedPtr reset_odom_server_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr base_connect_server_;

  // Publishers
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Publisher<rei_robot_base::msg::CarData>::SharedPtr car_data_pub_;
  std::vector<rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr> range_pubs_;

  // Subscribers
  rclcpp::Subscription<rei_robot_base::msg::MotorCmd>::SharedPtr motor_cmd_sub_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr vel_sub_;

  // Parameters
  float max_vel_x_;
  float max_vel_y_;
  float max_vel_th_;

  double odom_x_;
  double odom_y_;
  double odom_th_;

  bool publish_tf_;
  bool publish_odom_;
  bool soft_estop_;

  rclcpp::Time last_odom_time_;

  std::string robot_type_;
  std::string odom_frame_;
  std::string base_frame_;
  std::vector<std::string> range_frame_;
  std::vector<int> output_io_;
  KinematicData kin_data_;
  BaseComParams communicate_params_;

  // TF broadcaster
  std::unique_ptr<tf2_ros::TransformBroadcaster> odom_br_;

 private:
  void MotorCmdCallback(const rei_robot_base::msg::MotorCmd::SharedPtr msg);
  void VelCallback(const geometry_msgs::msg::Twist::SharedPtr msg);

  bool SetIOCallback(const std::shared_ptr<rei_robot_base::srv::SetIO::Request> req,
                     std::shared_ptr<rei_robot_base::srv::SetIO::Response> res);
  bool SetRelayCallback(const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
                        std::shared_ptr<std_srvs::srv::SetBool::Response> res);
  bool ExtraMotorCallback(const std::shared_ptr<rei_robot_base::srv::Int8::Request> req,
                          std::shared_ptr<rei_robot_base::srv::Int8::Response> res);
  bool SetBuzzerCallback(const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
                         std::shared_ptr<std_srvs::srv::SetBool::Response> res);
  bool ResetOdomCallback(const std::shared_ptr<std_srvs::srv::Empty::Request> req,
                         std::shared_ptr<std_srvs::srv::Empty::Response> res);
  bool BaseConnectCallback(const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
                           std::shared_ptr<std_srvs::srv::SetBool::Response> res);

  void VelLimit(float& vx, float& vy, float& vth);
};

}  // namespace reinovo_base
