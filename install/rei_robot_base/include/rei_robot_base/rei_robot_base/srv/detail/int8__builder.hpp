// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rei_robot_base:srv/Int8.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__INT8__BUILDER_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__INT8__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rei_robot_base/srv/detail/int8__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rei_robot_base
{

namespace srv
{

namespace builder
{

class Init_Int8_Request_data
{
public:
  Init_Int8_Request_data()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::rei_robot_base::srv::Int8_Request data(::rei_robot_base::srv::Int8_Request::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::srv::Int8_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::srv::Int8_Request>()
{
  return rei_robot_base::srv::builder::Init_Int8_Request_data();
}

}  // namespace rei_robot_base


namespace rei_robot_base
{

namespace srv
{

namespace builder
{

class Init_Int8_Response_message
{
public:
  explicit Init_Int8_Response_message(::rei_robot_base::srv::Int8_Response & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::srv::Int8_Response message(::rei_robot_base::srv::Int8_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::srv::Int8_Response msg_;
};

class Init_Int8_Response_success
{
public:
  Init_Int8_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Int8_Response_message success(::rei_robot_base::srv::Int8_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_Int8_Response_message(msg_);
  }

private:
  ::rei_robot_base::srv::Int8_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::srv::Int8_Response>()
{
  return rei_robot_base::srv::builder::Init_Int8_Response_success();
}

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__SRV__DETAIL__INT8__BUILDER_HPP_
