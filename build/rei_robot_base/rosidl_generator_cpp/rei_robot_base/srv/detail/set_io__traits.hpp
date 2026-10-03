// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rei_robot_base:srv/SetIO.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__SET_IO__TRAITS_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__SET_IO__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rei_robot_base/srv/detail/set_io__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace rei_robot_base
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetIO_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: all_off
  {
    out << "all_off: ";
    rosidl_generator_traits::value_to_yaml(msg.all_off, out);
    out << ", ";
  }

  // member: all_on
  {
    out << "all_on: ";
    rosidl_generator_traits::value_to_yaml(msg.all_on, out);
    out << ", ";
  }

  // member: io
  {
    if (msg.io.size() == 0) {
      out << "io: []";
    } else {
      out << "io: [";
      size_t pending_items = msg.io.size();
      for (auto item : msg.io) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetIO_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: all_off
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "all_off: ";
    rosidl_generator_traits::value_to_yaml(msg.all_off, out);
    out << "\n";
  }

  // member: all_on
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "all_on: ";
    rosidl_generator_traits::value_to_yaml(msg.all_on, out);
    out << "\n";
  }

  // member: io
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.io.size() == 0) {
      out << "io: []\n";
    } else {
      out << "io:\n";
      for (auto item : msg.io) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetIO_Request & msg, bool use_flow_style = false)
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
  const rei_robot_base::srv::SetIO_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::srv::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::srv::SetIO_Request & msg)
{
  return rei_robot_base::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::srv::SetIO_Request>()
{
  return "rei_robot_base::srv::SetIO_Request";
}

template<>
inline const char * name<rei_robot_base::srv::SetIO_Request>()
{
  return "rei_robot_base/srv/SetIO_Request";
}

template<>
struct has_fixed_size<rei_robot_base::srv::SetIO_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rei_robot_base::srv::SetIO_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rei_robot_base::srv::SetIO_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rei_robot_base
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetIO_Response & msg,
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
  const SetIO_Response & msg,
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

inline std::string to_yaml(const SetIO_Response & msg, bool use_flow_style = false)
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
  const rei_robot_base::srv::SetIO_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::srv::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::srv::SetIO_Response & msg)
{
  return rei_robot_base::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::srv::SetIO_Response>()
{
  return "rei_robot_base::srv::SetIO_Response";
}

template<>
inline const char * name<rei_robot_base::srv::SetIO_Response>()
{
  return "rei_robot_base/srv/SetIO_Response";
}

template<>
struct has_fixed_size<rei_robot_base::srv::SetIO_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rei_robot_base::srv::SetIO_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rei_robot_base::srv::SetIO_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rei_robot_base::srv::SetIO>()
{
  return "rei_robot_base::srv::SetIO";
}

template<>
inline const char * name<rei_robot_base::srv::SetIO>()
{
  return "rei_robot_base/srv/SetIO";
}

template<>
struct has_fixed_size<rei_robot_base::srv::SetIO>
  : std::integral_constant<
    bool,
    has_fixed_size<rei_robot_base::srv::SetIO_Request>::value &&
    has_fixed_size<rei_robot_base::srv::SetIO_Response>::value
  >
{
};

template<>
struct has_bounded_size<rei_robot_base::srv::SetIO>
  : std::integral_constant<
    bool,
    has_bounded_size<rei_robot_base::srv::SetIO_Request>::value &&
    has_bounded_size<rei_robot_base::srv::SetIO_Response>::value
  >
{
};

template<>
struct is_service<rei_robot_base::srv::SetIO>
  : std::true_type
{
};

template<>
struct is_service_request<rei_robot_base::srv::SetIO_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rei_robot_base::srv::SetIO_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // REI_ROBOT_BASE__SRV__DETAIL__SET_IO__TRAITS_HPP_
