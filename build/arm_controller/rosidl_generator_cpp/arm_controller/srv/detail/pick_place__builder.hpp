// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from arm_controller:srv/PickPlace.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__BUILDER_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "arm_controller/srv/detail/pick_place__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_PickPlace_Request_pose
{
public:
  explicit Init_PickPlace_Request_pose(::arm_controller::srv::PickPlace_Request & msg)
  : msg_(msg)
  {}
  ::arm_controller::srv::PickPlace_Request pose(::arm_controller::srv::PickPlace_Request::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::PickPlace_Request msg_;
};

class Init_PickPlace_Request_mode
{
public:
  explicit Init_PickPlace_Request_mode(::arm_controller::srv::PickPlace_Request & msg)
  : msg_(msg)
  {}
  Init_PickPlace_Request_pose mode(::arm_controller::srv::PickPlace_Request::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_PickPlace_Request_pose(msg_);
  }

private:
  ::arm_controller::srv::PickPlace_Request msg_;
};

class Init_PickPlace_Request_number
{
public:
  Init_PickPlace_Request_number()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickPlace_Request_mode number(::arm_controller::srv::PickPlace_Request::_number_type arg)
  {
    msg_.number = std::move(arg);
    return Init_PickPlace_Request_mode(msg_);
  }

private:
  ::arm_controller::srv::PickPlace_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::PickPlace_Request>()
{
  return arm_controller::srv::builder::Init_PickPlace_Request_number();
}

}  // namespace arm_controller


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_PickPlace_Response_message
{
public:
  explicit Init_PickPlace_Response_message(::arm_controller::srv::PickPlace_Response & msg)
  : msg_(msg)
  {}
  ::arm_controller::srv::PickPlace_Response message(::arm_controller::srv::PickPlace_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::PickPlace_Response msg_;
};

class Init_PickPlace_Response_success
{
public:
  explicit Init_PickPlace_Response_success(::arm_controller::srv::PickPlace_Response & msg)
  : msg_(msg)
  {}
  Init_PickPlace_Response_message success(::arm_controller::srv::PickPlace_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_PickPlace_Response_message(msg_);
  }

private:
  ::arm_controller::srv::PickPlace_Response msg_;
};

class Init_PickPlace_Response_pose
{
public:
  Init_PickPlace_Response_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickPlace_Response_success pose(::arm_controller::srv::PickPlace_Response::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_PickPlace_Response_success(msg_);
  }

private:
  ::arm_controller::srv::PickPlace_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::PickPlace_Response>()
{
  return arm_controller::srv::builder::Init_PickPlace_Response_pose();
}

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__BUILDER_HPP_
