// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arm_controller:srv/RelativePos.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__TRAITS_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "arm_controller/srv/detail/relative_pos__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const RelativePos_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: dx
  {
    out << "dx: ";
    rosidl_generator_traits::value_to_yaml(msg.dx, out);
    out << ", ";
  }

  // member: dy
  {
    out << "dy: ";
    rosidl_generator_traits::value_to_yaml(msg.dy, out);
    out << ", ";
  }

  // member: dz
  {
    out << "dz: ";
    rosidl_generator_traits::value_to_yaml(msg.dz, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RelativePos_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: dx
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dx: ";
    rosidl_generator_traits::value_to_yaml(msg.dx, out);
    out << "\n";
  }

  // member: dy
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dy: ";
    rosidl_generator_traits::value_to_yaml(msg.dy, out);
    out << "\n";
  }

  // member: dz
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dz: ";
    rosidl_generator_traits::value_to_yaml(msg.dz, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RelativePos_Request & msg, bool use_flow_style = false)
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
  const arm_controller::srv::RelativePos_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::RelativePos_Request & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::RelativePos_Request>()
{
  return "arm_controller::srv::RelativePos_Request";
}

template<>
inline const char * name<arm_controller::srv::RelativePos_Request>()
{
  return "arm_controller/srv/RelativePos_Request";
}

template<>
struct has_fixed_size<arm_controller::srv::RelativePos_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<arm_controller::srv::RelativePos_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<arm_controller::srv::RelativePos_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const RelativePos_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RelativePos_Response & msg,
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

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RelativePos_Response & msg, bool use_flow_style = false)
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
  const arm_controller::srv::RelativePos_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::RelativePos_Response & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::RelativePos_Response>()
{
  return "arm_controller::srv::RelativePos_Response";
}

template<>
inline const char * name<arm_controller::srv::RelativePos_Response>()
{
  return "arm_controller/srv/RelativePos_Response";
}

template<>
struct has_fixed_size<arm_controller::srv::RelativePos_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<arm_controller::srv::RelativePos_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<arm_controller::srv::RelativePos_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<arm_controller::srv::RelativePos>()
{
  return "arm_controller::srv::RelativePos";
}

template<>
inline const char * name<arm_controller::srv::RelativePos>()
{
  return "arm_controller/srv/RelativePos";
}

template<>
struct has_fixed_size<arm_controller::srv::RelativePos>
  : std::integral_constant<
    bool,
    has_fixed_size<arm_controller::srv::RelativePos_Request>::value &&
    has_fixed_size<arm_controller::srv::RelativePos_Response>::value
  >
{
};

template<>
struct has_bounded_size<arm_controller::srv::RelativePos>
  : std::integral_constant<
    bool,
    has_bounded_size<arm_controller::srv::RelativePos_Request>::value &&
    has_bounded_size<arm_controller::srv::RelativePos_Response>::value
  >
{
};

template<>
struct is_service<arm_controller::srv::RelativePos>
  : std::true_type
{
};

template<>
struct is_service_request<arm_controller::srv::RelativePos_Request>
  : std::true_type
{
};

template<>
struct is_service_response<arm_controller::srv::RelativePos_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__TRAITS_HPP_
