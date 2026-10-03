// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__TRAITS_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rei_robot_base/msg/detail/car_data__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rei_robot_base
{

namespace msg
{

inline void to_flow_style_yaml(
  const CarData & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: motor_speed
  {
    if (msg.motor_speed.size() == 0) {
      out << "motor_speed: []";
    } else {
      out << "motor_speed: [";
      size_t pending_items = msg.motor_speed.size();
      for (auto item : msg.motor_speed) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: crash
  {
    if (msg.crash.size() == 0) {
      out << "crash: []";
    } else {
      out << "crash: [";
      size_t pending_items = msg.crash.size();
      for (auto item : msg.crash) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: cliff
  {
    if (msg.cliff.size() == 0) {
      out << "cliff: []";
    } else {
      out << "cliff: [";
      size_t pending_items = msg.cliff.size();
      for (auto item : msg.cliff) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: ultrasound
  {
    if (msg.ultrasound.size() == 0) {
      out << "ultrasound: []";
    } else {
      out << "ultrasound: [";
      size_t pending_items = msg.ultrasound.size();
      for (auto item : msg.ultrasound) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: smoke
  {
    out << "smoke: ";
    rosidl_generator_traits::value_to_yaml(msg.smoke, out);
    out << ", ";
  }

  // member: power_voltage
  {
    out << "power_voltage: ";
    rosidl_generator_traits::value_to_yaml(msg.power_voltage, out);
    out << ", ";
  }

  // member: is_charge
  {
    out << "is_charge: ";
    rosidl_generator_traits::value_to_yaml(msg.is_charge, out);
    out << ", ";
  }

  // member: tempareture
  {
    out << "tempareture: ";
    rosidl_generator_traits::value_to_yaml(msg.tempareture, out);
    out << ", ";
  }

  // member: relative_humidity
  {
    out << "relative_humidity: ";
    rosidl_generator_traits::value_to_yaml(msg.relative_humidity, out);
    out << ", ";
  }

  // member: input_io
  {
    if (msg.input_io.size() == 0) {
      out << "input_io: []";
    } else {
      out << "input_io: [";
      size_t pending_items = msg.input_io.size();
      for (auto item : msg.input_io) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: output_io
  {
    if (msg.output_io.size() == 0) {
      out << "output_io: []";
    } else {
      out << "output_io: [";
      size_t pending_items = msg.output_io.size();
      for (auto item : msg.output_io) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: relay_status
  {
    out << "relay_status: ";
    rosidl_generator_traits::value_to_yaml(msg.relay_status, out);
    out << ", ";
  }

  // member: connect_status
  {
    out << "connect_status: ";
    rosidl_generator_traits::value_to_yaml(msg.connect_status, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CarData & msg,
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

  // member: motor_speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.motor_speed.size() == 0) {
      out << "motor_speed: []\n";
    } else {
      out << "motor_speed:\n";
      for (auto item : msg.motor_speed) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: crash
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.crash.size() == 0) {
      out << "crash: []\n";
    } else {
      out << "crash:\n";
      for (auto item : msg.crash) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: cliff
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.cliff.size() == 0) {
      out << "cliff: []\n";
    } else {
      out << "cliff:\n";
      for (auto item : msg.cliff) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: ultrasound
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.ultrasound.size() == 0) {
      out << "ultrasound: []\n";
    } else {
      out << "ultrasound:\n";
      for (auto item : msg.ultrasound) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: smoke
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "smoke: ";
    rosidl_generator_traits::value_to_yaml(msg.smoke, out);
    out << "\n";
  }

  // member: power_voltage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "power_voltage: ";
    rosidl_generator_traits::value_to_yaml(msg.power_voltage, out);
    out << "\n";
  }

  // member: is_charge
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_charge: ";
    rosidl_generator_traits::value_to_yaml(msg.is_charge, out);
    out << "\n";
  }

  // member: tempareture
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "tempareture: ";
    rosidl_generator_traits::value_to_yaml(msg.tempareture, out);
    out << "\n";
  }

  // member: relative_humidity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "relative_humidity: ";
    rosidl_generator_traits::value_to_yaml(msg.relative_humidity, out);
    out << "\n";
  }

  // member: input_io
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.input_io.size() == 0) {
      out << "input_io: []\n";
    } else {
      out << "input_io:\n";
      for (auto item : msg.input_io) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: output_io
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.output_io.size() == 0) {
      out << "output_io: []\n";
    } else {
      out << "output_io:\n";
      for (auto item : msg.output_io) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: relay_status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "relay_status: ";
    rosidl_generator_traits::value_to_yaml(msg.relay_status, out);
    out << "\n";
  }

  // member: connect_status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "connect_status: ";
    rosidl_generator_traits::value_to_yaml(msg.connect_status, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CarData & msg, bool use_flow_style = false)
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
  const rei_robot_base::msg::CarData & msg,
  std::ostream & out, size_t indentation = 0)
{
  rei_robot_base::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rei_robot_base::msg::to_yaml() instead")]]
inline std::string to_yaml(const rei_robot_base::msg::CarData & msg)
{
  return rei_robot_base::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rei_robot_base::msg::CarData>()
{
  return "rei_robot_base::msg::CarData";
}

template<>
inline const char * name<rei_robot_base::msg::CarData>()
{
  return "rei_robot_base/msg/CarData";
}

template<>
struct has_fixed_size<rei_robot_base::msg::CarData>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rei_robot_base::msg::CarData>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rei_robot_base::msg::CarData>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__TRAITS_HPP_
