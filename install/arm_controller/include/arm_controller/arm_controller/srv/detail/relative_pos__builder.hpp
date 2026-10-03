// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from arm_controller:srv/RelativePos.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__BUILDER_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "arm_controller/srv/detail/relative_pos__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_RelativePos_Request_dz
{
public:
  explicit Init_RelativePos_Request_dz(::arm_controller::srv::RelativePos_Request & msg)
  : msg_(msg)
  {}
  ::arm_controller::srv::RelativePos_Request dz(::arm_controller::srv::RelativePos_Request::_dz_type arg)
  {
    msg_.dz = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::RelativePos_Request msg_;
};

class Init_RelativePos_Request_dy
{
public:
  explicit Init_RelativePos_Request_dy(::arm_controller::srv::RelativePos_Request & msg)
  : msg_(msg)
  {}
  Init_RelativePos_Request_dz dy(::arm_controller::srv::RelativePos_Request::_dy_type arg)
  {
    msg_.dy = std::move(arg);
    return Init_RelativePos_Request_dz(msg_);
  }

private:
  ::arm_controller::srv::RelativePos_Request msg_;
};

class Init_RelativePos_Request_dx
{
public:
  Init_RelativePos_Request_dx()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RelativePos_Request_dy dx(::arm_controller::srv::RelativePos_Request::_dx_type arg)
  {
    msg_.dx = std::move(arg);
    return Init_RelativePos_Request_dy(msg_);
  }

private:
  ::arm_controller::srv::RelativePos_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::RelativePos_Request>()
{
  return arm_controller::srv::builder::Init_RelativePos_Request_dx();
}

}  // namespace arm_controller


namespace arm_controller
{

namespace srv
{

namespace builder
{

class Init_RelativePos_Response_message
{
public:
  explicit Init_RelativePos_Response_message(::arm_controller::srv::RelativePos_Response & msg)
  : msg_(msg)
  {}
  ::arm_controller::srv::RelativePos_Response message(::arm_controller::srv::RelativePos_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::arm_controller::srv::RelativePos_Response msg_;
};

class Init_RelativePos_Response_success
{
public:
  Init_RelativePos_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RelativePos_Response_message success(::arm_controller::srv::RelativePos_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_RelativePos_Response_message(msg_);
  }

private:
  ::arm_controller::srv::RelativePos_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::arm_controller::srv::RelativePos_Response>()
{
  return arm_controller::srv::builder::Init_RelativePos_Response_success();
}

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__BUILDER_HPP_
