// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rei_robot_base:msg/MotorCmd.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__TRAITS_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rei_robot_base/msg/detail/motor_cmd__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rei_robot_base
{

namespace msg
{

inline void to_flow_style_yaml(
  const MotorCmd & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: motor_expect_speed
  {
    if (msg.motor_expect_speed.size() == 0) {
      out << "motor_expect_speed: []";
    } else {
      out << "motor_expect_speed: [";
      size_t pending_items = msg.motor_expect_speed.size();
      for (auto item : msg.motor_expect_speed) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MotorCmd & msg,
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

  // member: motor_expect_speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.motor_expect_speed.size() == 0) {
      out << "motor_expect_speed: []\n";
    } else {
      out << "motor_expect_speed:\n";
      for (auto item : msg.motor_expect_speed) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MotorCmd & msg, bool use_flow_style = false)
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
  const rei_robot_base::msg::MotorCmd & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::msg::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::msg::MotorCmd & msg)
{
  return rei_robot_base::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::msg::MotorCmd>()
{
  return "rei_robot_base::msg::MotorCmd";
}

template<>
inline const char * name<rei_robot_base::msg::MotorCmd>()
{
  return "rei_robot_base/msg/MotorCmd";
}

template<>
struct has_fixed_size<rei_robot_base::msg::MotorCmd>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rei_robot_base::msg::MotorCmd>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rei_robot_base::msg::MotorCmd>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__TRAITS_HPP_
