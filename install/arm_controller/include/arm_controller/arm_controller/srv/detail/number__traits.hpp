// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__NUMBER__TRAITS_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__NUMBER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "arm_controller/srv/detail/number__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const Number_Request & msg,
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
  const Number_Request & msg,
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

inline std::string to_yaml(const Number_Request & msg, bool use_flow_style = false)
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
  const arm_controller::srv::Number_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::Number_Request & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::Number_Request>()
{
  return "arm_controller::srv::Number_Request";
}

template<>
inline const char * name<arm_controller::srv::Number_Request>()
{
  return "arm_controller/srv/Number_Request";
}

template<>
struct has_fixed_size<arm_controller::srv::Number_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<arm_controller::srv::Number_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<arm_controller::srv::Number_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'pose'
#include "arm_controller/msg/detail/control__traits.hpp"

namespace arm_controller
{

namespace srv
{

inline void to_flow_style_yaml(
  const Number_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: number
  {
    if (msg.number.size() == 0) {
      out << "number: []";
    } else {
      out << "number: [";
      size_t pending_items = msg.number.size();
      for (auto item : msg.number) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: pose
  {
    if (msg.pose.size() == 0) {
      out << "pose: []";
    } else {
      out << "pose: [";
      size_t pending_items = msg.pose.size();
      for (auto item : msg.pose) {
        to_flow_style_yaml(item, out);
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
  const Number_Response & msg,
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

  // member: number
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.number.size() == 0) {
      out << "number: []\n";
    } else {
      out << "number:\n";
      for (auto item : msg.number) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.pose.size() == 0) {
      out << "pose: []\n";
    } else {
      out << "pose:\n";
      for (auto item : msg.pose) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Number_Response & msg, bool use_flow_style = false)
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
  const arm_controller::srv::Number_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  arm_controller::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use arm_controller::srv::to_yaml() instead")]]
inline std::string to_yaml(const arm_controller::srv::Number_Response & msg)
{
  return arm_controller::srv::to_yaml(msg);
}

template<>
inline const char * data_type<arm_controller::srv::Number_Response>()
{
  return "arm_controller::srv::Number_Response";
}

template<>
inline const char * name<arm_controller::srv::Number_Response>()
{
  return "arm_controller/srv/Number_Response";
}

template<>
struct has_fixed_size<arm_controller::srv::Number_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<arm_controller::srv::Number_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<arm_controller::srv::Number_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<arm_controller::srv::Number>()
{
  return "arm_controller::srv::Number";
}

template<>
inline const char * name<arm_controller::srv::Number>()
{
  return "arm_controller/srv/Number";
}

template<>
struct has_fixed_size<arm_controller::srv::Number>
  : std::integral_constant<
    bool,
    has_fixed_size<arm_controller::srv::Number_Request>::value &&
    has_fixed_size<arm_controller::srv::Number_Response>::value
  >
{
};

template<>
struct has_bounded_size<arm_controller::srv::Number>
  : std::integral_constant<
    bool,
    has_bounded_size<arm_controller::srv::Number_Request>::value &&
    has_bounded_size<arm_controller::srv::Number_Response>::value
  >
{
};

template<>
struct is_service<arm_controller::srv::Number>
  : std::true_type
{
};

template<>
struct is_service_request<arm_controller::srv::Number_Request>
  : std::true_type
{
};

template<>
struct is_service_response<arm_controller::srv::Number_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ARM_CONTROLLER__SRV__DETAIL__NUMBER__TRAITS_HPP_
