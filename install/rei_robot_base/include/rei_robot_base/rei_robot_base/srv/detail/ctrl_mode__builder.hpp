// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__BUILDER_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rei_robot_base/srv/detail/ctrl_mode__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rei_robot_base
{

namespace srv
{

namespace builder
{

class Init_CtrlMode_Request_use_acc
{
public:
  explicit Init_CtrlMode_Request_use_acc(::rei_robot_base::srv::CtrlMode_Request & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::srv::CtrlMode_Request use_acc(::rei_robot_base::srv::CtrlMode_Request::_use_acc_type arg)
  {
    msg_.use_acc = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::srv::CtrlMode_Request msg_;
};

class Init_CtrlMode_Request_ctrl_mode
{
public:
  Init_CtrlMode_Request_ctrl_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CtrlMode_Request_use_acc ctrl_mode(::rei_robot_base::srv::CtrlMode_Request::_ctrl_mode_type arg)
  {
    msg_.ctrl_mode = std::move(arg);
    return Init_CtrlMode_Request_use_acc(msg_);
  }

private:
  ::rei_robot_base::srv::CtrlMode_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::srv::CtrlMode_Request>()
{
  return rei_robot_base::srv::builder::Init_CtrlMode_Request_ctrl_mode();
}

}  // namespace rei_robot_base


namespace rei_robot_base
{

namespace srv
{

namespace builder
{

class Init_CtrlMode_Response_success
{
public:
  Init_CtrlMode_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::rei_robot_base::srv::CtrlMode_Response success(::rei_robot_base::srv::CtrlMode_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::srv::CtrlMode_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::srv::CtrlMode_Response>()
{
  return rei_robot_base::srv::builder::Init_CtrlMode_Response_success();
}

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__BUILDER_HPP_
