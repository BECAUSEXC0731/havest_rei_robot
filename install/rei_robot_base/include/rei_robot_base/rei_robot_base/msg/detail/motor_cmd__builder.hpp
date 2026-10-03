// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rei_robot_base:msg/MotorCmd.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__BUILDER_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rei_robot_base/msg/detail/motor_cmd__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rei_robot_base
{

namespace msg
{

namespace builder
{

class Init_MotorCmd_motor_expect_speed
{
public:
  explicit Init_MotorCmd_motor_expect_speed(::rei_robot_base::msg::MotorCmd & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::msg::MotorCmd motor_expect_speed(::rei_robot_base::msg::MotorCmd::_motor_expect_speed_type arg)
  {
    msg_.motor_expect_speed = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::msg::MotorCmd msg_;
};

class Init_MotorCmd_header
{
public:
  Init_MotorCmd_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorCmd_motor_expect_speed header(::rei_robot_base::msg::MotorCmd::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_MotorCmd_motor_expect_speed(msg_);
  }

private:
  ::rei_robot_base::msg::MotorCmd msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::msg::MotorCmd>()
{
  return rei_robot_base::msg::builder::Init_MotorCmd_header();
}

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__BUILDER_HPP_
