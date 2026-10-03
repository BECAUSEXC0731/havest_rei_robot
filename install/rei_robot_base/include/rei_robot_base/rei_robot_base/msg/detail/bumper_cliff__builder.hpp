// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rei_robot_base:msg/BumperCliff.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__BUILDER_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rei_robot_base/msg/detail/bumper_cliff__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rei_robot_base
{

namespace msg
{

namespace builder
{

class Init_BumperCliff_cliff
{
public:
  explicit Init_BumperCliff_cliff(::rei_robot_base::msg::BumperCliff & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::msg::BumperCliff cliff(::rei_robot_base::msg::BumperCliff::_cliff_type arg)
  {
    msg_.cliff = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::msg::BumperCliff msg_;
};

class Init_BumperCliff_bumper
{
public:
  explicit Init_BumperCliff_bumper(::rei_robot_base::msg::BumperCliff & msg)
  : msg_(msg)
  {}
  Init_BumperCliff_cliff bumper(::rei_robot_base::msg::BumperCliff::_bumper_type arg)
  {
    msg_.bumper = std::move(arg);
    return Init_BumperCliff_cliff(msg_);
  }

private:
  ::rei_robot_base::msg::BumperCliff msg_;
};

class Init_BumperCliff_header
{
public:
  Init_BumperCliff_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_BumperCliff_bumper header(::rei_robot_base::msg::BumperCliff::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_BumperCliff_bumper(msg_);
  }

private:
  ::rei_robot_base::msg::BumperCliff msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::msg::BumperCliff>()
{
  return rei_robot_base::msg::builder::Init_BumperCliff_header();
}

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__BUILDER_HPP_
