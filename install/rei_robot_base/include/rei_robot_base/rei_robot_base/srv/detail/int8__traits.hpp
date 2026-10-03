// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rei_robot_base:srv/Int8.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__INT8__TRAITS_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__INT8__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rei_robot_base/srv/detail/int8__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace rei_robot_base
{

namespace srv
{

inline void to_flow_style_yaml(
  const Int8_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: data
  {
    out << "data: ";
    rosidl_generator_traits::value_to_yaml(msg.data, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Int8_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "data: ";
    rosidl_generator_traits::value_to_yaml(msg.data, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Int8_Request & msg, bool use_flow_style = false)
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
  const rei_robot_base::srv::Int8_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::srv::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::srv::Int8_Request & msg)
{
  return rei_robot_base::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::srv::Int8_Request>()
{
  return "rei_robot_base::srv::Int8_Request";
}

template<>
inline const char * name<rei_robot_base::srv::Int8_Request>()
{
  return "rei_robot_base/srv/Int8_Request";
}

template<>
struct has_fixed_size<rei_robot_base::srv::Int8_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rei_robot_base::srv::Int8_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rei_robot_base::srv::Int8_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rei_robot_base
{

namespace srv
{

inline void to_flow_style_yaml(
  const Int8_Response & msg,
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
  const Int8_Response & msg,
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

inline std::string to_yaml(const Int8_Response & msg, bool use_flow_style = false)
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
  const rei_robot_base::srv::Int8_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::srv::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::srv::Int8_Response & msg)
{
  return rei_robot_base::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::srv::Int8_Response>()
{
  return "rei_robot_base::srv::Int8_Response";
}

template<>
inline const char * name<rei_robot_base::srv::Int8_Response>()
{
  return "rei_robot_base/srv/Int8_Response";
}

template<>
struct has_fixed_size<rei_robot_base::srv::Int8_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rei_robot_base::srv::Int8_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rei_robot_base::srv::Int8_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rei_robot_base::srv::Int8>()
{
  return "rei_robot_base::srv::Int8";
}

template<>
inline const char * name<rei_robot_base::srv::Int8>()
{
  return "rei_robot_base/srv/Int8";
}

template<>
struct has_fixed_size<rei_robot_base::srv::Int8>
  : std::integral_constant<
    bool,
    has_fixed_size<rei_robot_base::srv::Int8_Request>::value &&
    has_fixed_size<rei_robot_base::srv::Int8_Response>::value
  >
{
};

template<>
struct has_bounded_size<rei_robot_base::srv::Int8>
  : std::integral_constant<
    bool,
    has_bounded_size<rei_robot_base::srv::Int8_Request>::value &&
    has_bounded_size<rei_robot_base::srv::Int8_Response>::value
  >
{
};

template<>
struct is_service<rei_robot_base::srv::Int8>
  : std::true_type
{
};

template<>
struct is_service_request<rei_robot_base::srv::Int8_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rei_robot_base::srv::Int8_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // REI_ROBOT_BASE__SRV__DETAIL__INT8__TRAITS_HPP_
