// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from arm_controller:srv/Move.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__MOVE__BUILDER_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__MOVE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "arm_controller/srv/detail/move__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_Move_Request_pose
{
public:
  Init_Move_Request_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::arm_controller::srv::Move_Request pose(::arm_controller::srv::Move_Request::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::Move_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::Move_Request>()
{
  return arm_controller::srv::builder::Init_Move_Request_pose();
}

}  // namespace arm_controller


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_Move_Response_success
{
public:
  explicit Init_Move_Response_success(::arm_controller::srv::Move_Response & msg)
  : msg_(msg)
  {}
  ::arm_controller::srv::Move_Response success(::arm_controller::srv::Move_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::Move_Response msg_;
};

class Init_Move_Response_message
{
public:
  Init_Move_Response_message()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Move_Response_success message(::arm_controller::srv::Move_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return Init_Move_Response_success(msg_);
  }

private:
  ::arm_controller::srv::Move_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::Move_Response>()
{
  return arm_controller::srv::builder::Init_Move_Response_message();
}

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__MOVE__BUILDER_HPP_
