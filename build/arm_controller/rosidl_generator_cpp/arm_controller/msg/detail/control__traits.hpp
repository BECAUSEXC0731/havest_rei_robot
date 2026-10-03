// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arm_controller:msg/Control.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__MSG__DETAIL__CONTROL__TRAITS_HPP_
#define ARM_CONTROLLER__MSG__DETAIL__CONTROL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "arm_controller/msg/detail/control__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'position'
#include "geometry_msgs/msg/detail/point__traits.hpp"

namespace arm_controller
{

namespace msg
{

inline void to_flow_style_yaml(
  const Control & msg,
  std::ostream & out)
{
  out << "{";
  // member: position
  {
    out << "position: ";
    to_flow_style_yaml(msg.position, out);
    out << ", ";
  }

  // member: roll
  {
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << ", ";
  }

  // member: pitch
  {
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << ", ";
  }

  // member: yaw
  {
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Control & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: position
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "position:\n";
    to_block_style_yaml(msg.position, out, indentation + 2);
  }

  // member: roll
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << "\n";
  }

  // member: pitch
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << "\n";
  }

  // member: yaw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Control & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace arm_controller

namespace rosidl_generator_traits
{

[[deprecated("use arm_controller::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const arm_controller::msg::Control & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::msg::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::msg::Control & msg)
{
  return arm_controller::msg::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::msg::Control>()
{
  return "arm_controller::msg::Control";
}

template<>
inline const char * name<arm_controller::msg::Control>()
{
  return "arm_controller/msg/Control";
}

template<>
struct has_fixed_size<arm_controller::msg::Control>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::Point>::value> {};

template<>
struct has_bounded_size<arm_controller::msg::Control>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::Point>::value> {};

template<>
struct is_message<arm_controller::msg::Control>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ARM_CONTROLLER__MSG__DETAIL__CONTROL__TRAITS_HPP_
