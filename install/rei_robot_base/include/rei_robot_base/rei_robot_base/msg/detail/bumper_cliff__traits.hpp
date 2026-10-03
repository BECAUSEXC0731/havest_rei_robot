// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rei_robot_base:msg/BumperCliff.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__TRAITS_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rei_robot_base/msg/detail/bumper_cliff__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rei_robot_base
{

namespace msg
{

inline void to_flow_style_yaml(
  const BumperCliff & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: bumper
  {
    out << "bumper: ";
    rosidl_generator_traits::value_to_yaml(msg.bumper, out);
    out << ", ";
  }

  // member: cliff
  {
    out << "cliff: ";
    rosidl_generator_traits::value_to_yaml(msg.cliff, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const BumperCliff & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: bumper
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bumper: ";
    rosidl_generator_traits::value_to_yaml(msg.bumper, out);
    out << "\n";
  }

  // member: cliff
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cliff: ";
    rosidl_generator_traits::value_to_yaml(msg.cliff, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const BumperCliff & msg, bool use_flow_style = false)
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

}  // namespace rei_robot_base

namespace rosidl_generator_traits
{

[[deprecated("use rei_robot_base::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rei_robot_base::msg::BumperCliff & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::msg::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::msg::BumperCliff & msg)
{
  return rei_robot_base::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::msg::BumperCliff>()
{
  return "rei_robot_base::msg::BumperCliff";
}

template<>
inline const char * name<rei_robot_base::msg::BumperCliff>()
{
  return "rei_robot_base/msg/BumperCliff";
}

template<>
struct has_fixed_size<rei_robot_base::msg::BumperCliff>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<rei_robot_base::msg::BumperCliff>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<rei_robot_base::msg::BumperCliff>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__TRAITS_HPP_
