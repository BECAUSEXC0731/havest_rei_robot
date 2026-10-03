// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from arm_controller:msg/Control.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__MSG__DETAIL__CONTROL__BUILDER_HPP_
#define ARM_CONTROLLER__MSG__DETAIL__CONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "arm_controller/msg/detail/control__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace arm_controller
{

namespace msg
{

namespace builder
{

class Init_Control_yaw
{
public:
  explicit Init_Control_yaw(::arm_controller::msg::Control & msg)
  : msg_(msg)
  {}
  ::arm_controller::msg::Control yaw(::arm_controller::msg::Control::_yaw_type arg)
  {
    msg_.yaw = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::msg::Control msg_;
};

class Init_Control_pitch
{
public:
  explicit Init_Control_pitch(::arm_controller::msg::Control & msg)
  : msg_(msg)
  {}
  Init_Control_yaw pitch(::arm_controller::msg::Control::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_Control_yaw(msg_);
  }

private:
  ::arm_controller::msg::Control msg_;
};

class Init_Control_roll
{
public:
  explicit Init_Control_roll(::arm_controller::msg::Control & msg)
  : msg_(msg)
  {}
  Init_Control_pitch roll(::arm_controller::msg::Control::_roll_type arg)
  {
    msg_.roll = std::move(arg);
    return Init_Control_pitch(msg_);
  }

private:
  ::arm_controller::msg::Control msg_;
};

class Init_Control_position
{
public:
  Init_Control_position()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Control_roll position(::arm_controller::msg::Control::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_Control_roll(msg_);
  }

private:
  ::arm_controller::msg::Control msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::msg::Control>()
{
  return arm_controller::msg::builder::Init_Control_position();
}

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__MSG__DETAIL__CONTROL__BUILDER_HPP_
