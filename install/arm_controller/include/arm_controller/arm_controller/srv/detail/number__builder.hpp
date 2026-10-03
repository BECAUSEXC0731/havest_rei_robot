// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__NUMBER__BUILDER_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__NUMBER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "arm_controller/srv/detail/number__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_Number_Request_data
{
public:
  Init_Number_Request_data()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::arm_controller::srv::Number_Request data(::arm_controller::srv::Number_Request::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::Number_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::Number_Request>()
{
  return arm_controller::srv::builder::Init_Number_Request_data();
}

}  // namespace arm_controller


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_Number_Response_pose
{
public:
  explicit Init_Number_Response_pose(::arm_controller::srv::Number_Response & msg)
  : msg_(msg)
  {}
  ::arm_controller::srv::Number_Response pose(::arm_controller::srv::Number_Response::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::Number_Response msg_;
};

class Init_Number_Response_number
{
public:
  explicit Init_Number_Response_number(::arm_controller::srv::Number_Response & msg)
  : msg_(msg)
  {}
  Init_Number_Response_pose number(::arm_controller::srv::Number_Response::_number_type arg)
  {
    msg_.number = std::move(arg);
    return Init_Number_Response_pose(msg_);
  }

private:
  ::arm_controller::srv::Number_Response msg_;
};

class Init_Number_Response_success
{
public:
  Init_Number_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Number_Response_number success(::arm_controller::srv::Number_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_Number_Response_number(msg_);
  }

private:
  ::arm_controller::srv::Number_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::Number_Response>()
{
  return arm_controller::srv::builder::Init_Number_Response_success();
}

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__NUMBER__BUILDER_HPP_
