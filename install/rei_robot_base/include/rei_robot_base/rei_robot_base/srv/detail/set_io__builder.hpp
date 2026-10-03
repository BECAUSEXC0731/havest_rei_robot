// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rei_robot_base:srv/SetIO.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__SET_IO__BUILDER_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__SET_IO__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rei_robot_base/srv/detail/set_io__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rei_robot_base
{

namespace srv
{

namespace builder
{

class Init_SetIO_Request_state
{
public:
  explicit Init_SetIO_Request_state(::rei_robot_base::srv::SetIO_Request & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::srv::SetIO_Request state(::rei_robot_base::srv::SetIO_Request::_state_type arg)
  {
    msg_.state = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::srv::SetIO_Request msg_;
};

class Init_SetIO_Request_io
{
public:
  explicit Init_SetIO_Request_io(::rei_robot_base::srv::SetIO_Request & msg)
  : msg_(msg)
  {}
  Init_SetIO_Request_state io(::rei_robot_base::srv::SetIO_Request::_io_type arg)
  {
    msg_.io = std::move(arg);
    return Init_SetIO_Request_state(msg_);
  }

private:
  ::rei_robot_base::srv::SetIO_Request msg_;
};

class Init_SetIO_Request_all_on
{
public:
  explicit Init_SetIO_Request_all_on(::rei_robot_base::srv::SetIO_Request & msg)
  : msg_(msg)
  {}
  Init_SetIO_Request_io all_on(::rei_robot_base::srv::SetIO_Request::_all_on_type arg)
  {
    msg_.all_on = std::move(arg);
    return Init_SetIO_Request_io(msg_);
  }

private:
  ::rei_robot_base::srv::SetIO_Request msg_;
};

class Init_SetIO_Request_all_off
{
public:
  Init_SetIO_Request_all_off()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetIO_Request_all_on all_off(::rei_robot_base::srv::SetIO_Request::_all_off_type arg)
  {
    msg_.all_off = std::move(arg);
    return Init_SetIO_Request_all_on(msg_);
  }

private:
  ::rei_robot_base::srv::SetIO_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::srv::SetIO_Request>()
{
  return rei_robot_base::srv::builder::Init_SetIO_Request_all_off();
}

}  // namespace rei_robot_base


namespace rei_robot_base
{

namespace srv
{

namespace builder
{

class Init_SetIO_Response_message
{
public:
  explicit Init_SetIO_Response_message(::rei_robot_base::srv::SetIO_Response & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::srv::SetIO_Response message(::rei_robot_base::srv::SetIO_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::srv::SetIO_Response msg_;
};

class Init_SetIO_Response_success
{
public:
  Init_SetIO_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetIO_Response_message success(::rei_robot_base::srv::SetIO_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_SetIO_Response_message(msg_);
  }

private:
  ::rei_robot_base::srv::SetIO_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::srv::SetIO_Response>()
{
  return rei_robot_base::srv::builder::Init_SetIO_Response_success();
}

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__SRV__DETAIL__SET_IO__BUILDER_HPP_
