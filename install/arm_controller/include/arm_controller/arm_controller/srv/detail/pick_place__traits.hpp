// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arm_controller:srv/PickPlace.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__TRAITS_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "arm_controller/srv/detail/pick_place__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "arm_controller/msg/detail/control__traits.hpp"

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const PickPlace_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: number
  {
    out << "number: ";
    rosidl_generator_traits::value_to_yaml(msg.number, out);
    out << ", ";
  }

  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << ", ";
  }

  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickPlace_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: number
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "number: ";
    rosidl_generator_traits::value_to_yaml(msg.number, out);
    out << "\n";
  }

  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }

  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickPlace_Request & msg, bool use_flow_style = false)
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
  const arm_controller::srv::PickPlace_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::PickPlace_Request & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::PickPlace_Request>()
{
  return "arm_controller::srv::PickPlace_Request";
}

template<>
inline const char * name<arm_controller::srv::PickPlace_Request>()
{
  return "arm_controller/srv/PickPlace_Request";
}

template<>
struct has_fixed_size<arm_controller::srv::PickPlace_Request>
  : std::integral_constant<bool, has_fixed_size<arm_controller::msg::Control>::value> {};

template<>
struct has_bounded_size<arm_controller::srv::PickPlace_Request>
  : std::integral_constant<bool, has_bounded_size<arm_controller::msg::Control>::value> {};

template<>
struct is_message<arm_controller::srv::PickPlace_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'pose'
// already included above
// #include "arm_controller/msg/detail/control__traits.hpp"

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const PickPlace_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
    out << ", ";
  }

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
  const PickPlace_Response & msg,
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

inline std::string to_yaml(const PickPlace_Response & msg, bool use_flow_style = false)
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
  const arm_controller::srv::PickPlace_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::PickPlace_Response & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::PickPlace_Response>()
{
  return "arm_controller::srv::PickPlace_Response";
}

template<>
inline const char * name<arm_controller::srv::PickPlace_Response>()
{
  return "arm_controller/srv/PickPlace_Response";
}

template<>
struct has_fixed_size<arm_controller::srv::PickPlace_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<arm_controller::srv::PickPlace_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<arm_controller::srv::PickPlace_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<arm_controller::srv::PickPlace>()
{
  return "arm_controller::srv::PickPlace";
}

template<>
inline const char * name<arm_controller::srv::PickPlace>()
{
  return "arm_controller/srv/PickPlace";
}

template<>
struct has_fixed_size<arm_controller::srv::PickPlace>
  : std::integral_constant<
    bool,
    has_fixed_size<arm_controller::srv::PickPlace_Request>::value &&
    has_fixed_size<arm_controller::srv::PickPlace_Response>::value
  >
{
};

template<>
struct has_bounded_size<arm_controller::srv::PickPlace>
  : std::integral_constant<
    bool,
    has_bounded_size<arm_controller::srv::PickPlace_Request>::value &&
    has_bounded_size<arm_controller::srv::PickPlace_Response>::value
  >
{
};

template<>
struct is_service<arm_controller::srv::PickPlace>
  : std::true_type
{
};

template<>
struct is_service_request<arm_controller::srv::PickPlace_Request>
  : std::true_type
{
};

template<>
struct is_service_response<arm_controller::srv::PickPlace_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__TRAITS_HPP_
