// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arm_controller:srv/Move.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__MOVE__TRAITS_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__MOVE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "arm_controller/srv/detail/move__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "arm_controller/msg/detail/control__traits.hpp"

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const Move_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Move_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Move_Request & msg, bool use_flow_style = false)
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

}  // namespace arm_controller

namespace rosidl_generator_traits
{

[[deprecated("use arm_controller::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const arm_controller::srv::Move_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::Move_Request & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::Move_Request>()
{
  return "arm_controller::srv::Move_Request";
}

template<>
inline const char * name<arm_controller::srv::Move_Request>()
{
  return "arm_controller/srv/Move_Request";
}

template<>
struct has_fixed_size<arm_controller::srv::Move_Request>
  : std::integral_constant<bool, has_fixed_size<arm_controller::msg::Control>::value> {};

template<>
struct has_bounded_size<arm_controller::srv::Move_Request>
  : std::integral_constant<bool, has_bounded_size<arm_controller::msg::Control>::value> {};

template<>
struct is_message<arm_controller::srv::Move_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const Move_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << ", ";
  }

  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Move_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }

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

inline std::string to_yaml(const Move_Response & msg, bool use_flow_style = false)
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

}  // namespace arm_controller

namespace rosidl_generator_traits
{

[[deprecated("use arm_controller::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const arm_controller::srv::Move_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::Move_Response & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::Move_Response>()
{
  return "arm_controller::srv::Move_Response";
}

template<>
inline const char * name<arm_controller::srv::Move_Response>()
{
  return "arm_controller/srv/Move_Response";
}

template<>
struct has_fixed_size<arm_controller::srv::Move_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<arm_controller::srv::Move_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<arm_controller::srv::Move_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<arm_controller::srv::Move>()
{
  return "arm_controller::srv::Move";
}

template<>
inline const char * name<arm_controller::srv::Move>()
{
  return "arm_controller/srv/Move";
}

template<>
struct has_fixed_size<arm_controller::srv::Move>
  : std::integral_constant<
    bool,
    has_fixed_size<arm_controller::srv::Move_Request>::value &&
    has_fixed_size<arm_controller::srv::Move_Response>::value
  >
{
};

template<>
struct has_bounded_size<arm_controller::srv::Move>
  : std::integral_constant<
    bool,
    has_bounded_size<arm_controller::srv::Move_Request>::value &&
    has_bounded_size<arm_controller::srv::Move_Response>::value
  >
{
};

template<>
struct is_service<arm_controller::srv::Move>
  : std::true_type
{
};

template<>
struct is_service_request<arm_controller::srv::Move_Request>
  : std::true_type
{
};

template<>
struct is_service_response<arm_controller::srv::Move_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ARM_CONTROLLER__SRV__DETAIL__MOVE__TRAITS_HPP_
