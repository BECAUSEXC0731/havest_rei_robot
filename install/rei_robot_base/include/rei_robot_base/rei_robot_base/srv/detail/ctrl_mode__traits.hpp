// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__TRAITS_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rei_robot_base/srv/detail/ctrl_mode__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace rei_robot_base
{

namespace srv
{

inline void to_flow_style_yaml(
  const CtrlMode_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: ctrl_mode
  {
    out << "ctrl_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.ctrl_mode, out);
    out << ", ";
  }

  // member: use_acc
  {
    out << "use_acc: ";
    rosidl_generator_traits::value_to_yaml(msg.use_acc, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CtrlMode_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: ctrl_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ctrl_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.ctrl_mode, out);
    out << "\n";
  }

  // member: use_acc
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "use_acc: ";
    rosidl_generator_traits::value_to_yaml(msg.use_acc, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CtrlMode_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace rei_robot_base

namespace rosidl_generator_traits
{

[[deprecated("use rei_robot_base::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rei_robot_base::srv::CtrlMode_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::srv::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::srv::CtrlMode_Request & msg)
{
  return rei_robot_base::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::srv::CtrlMode_Request>()
{
  return "rei_robot_base::srv::CtrlMode_Request";
}

template<>
inline const char * name<rei_robot_base::srv::CtrlMode_Request>()
{
  return "rei_robot_base/srv/CtrlMode_Request";
}

template<>
struct has_fixed_size<rei_robot_base::srv::CtrlMode_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rei_robot_base::srv::CtrlMode_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rei_robot_base::srv::CtrlMode_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rei_robot_base
{

namespace srv
{

inline void to_flow_style_yaml(
  const CtrlMode_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CtrlMode_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CtrlMode_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace rei_robot_base

namespace rosidl_generator_traits
{

[[deprecated("use rei_robot_base::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rei_robot_base::srv::CtrlMode_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::srv::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::srv::CtrlMode_Response & msg)
{
  return rei_robot_base::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::srv::CtrlMode_Response>()
{
  return "rei_robot_base::srv::CtrlMode_Response";
}

template<>
inline const char * name<rei_robot_base::srv::CtrlMode_Response>()
{
  return "rei_robot_base/srv/CtrlMode_Response";
}

template<>
struct has_fixed_size<rei_robot_base::srv::CtrlMode_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rei_robot_base::srv::CtrlMode_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rei_robot_base::srv::CtrlMode_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rei_robot_base::srv::CtrlMode>()
{
  return "rei_robot_base::srv::CtrlMode";
}

template<>
inline const char * name<rei_robot_base::srv::CtrlMode>()
{
  return "rei_robot_base/srv/CtrlMode";
}

template<>
struct has_fixed_size<rei_robot_base::srv::CtrlMode>
  : std::integral_constant<
    bool,
    has_fixed_size<rei_robot_base::srv::CtrlMode_Request>::value &&
    has_fixed_size<rei_robot_base::srv::CtrlMode_Response>::value
  >
{
};

template<>
struct has_bounded_size<rei_robot_base::srv::CtrlMode>
  : std::integral_constant<
    bool,
    has_bounded_size<rei_robot_base::srv::CtrlMode_Request>::value &&
    has_bounded_size<rei_robot_base::srv::CtrlMode_Response>::value
  >
{
};

template<>
struct is_service<rei_robot_base::srv::CtrlMode>
  : std::true_type
{
};

template<>
struct is_service_request<rei_robot_base::srv::CtrlMode_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rei_robot_base::srv::CtrlMode_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__TRAITS_HPP_
