// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/msg/detail/car_data__rosidl_typesupport_fastrtps_cpp.hpp"
#include "rei_robot_base/msg/detail/car_data__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions
namespace std_msgs
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const std_msgs::msg::Header &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  std_msgs::msg::Header &);
size_t get_serialized_size(
  const std_msgs::msg::Header &,
  size_t current_alignment);
size_t
max_serialized_size_Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace std_msgs


namespace rei_robot_base
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rei_robot_base
cdr_serialize(
  const rei_robot_base::msg::CarData & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.header,
    cdr);
  // Member: motor_speed
  {
    cdr << ros_message.motor_speed;
  }
  // Member: crash
  {
    cdr << ros_message.crash;
  }
  // Member: cliff
  {
    cdr << ros_message.cliff;
  }
  // Member: ultrasound
  {
    cdr << ros_message.ultrasound;
  }
  // Member: smoke
  cdr << ros_message.smoke;
  // Member: power_voltage
  cdr << ros_message.power_voltage;
  // Member: is_charge
  cdr << (ros_message.is_charge ? true : false);
  // Member: tempareture
  cdr << ros_message.tempareture;
  // Member: relative_humidity
  cdr << ros_message.relative_humidity;
  // Member: input_io
  {
    cdr << ros_message.input_io;
  }
  // Member: output_io
  {
    cdr << ros_message.output_io;
  }
  // Member: relay_status
  cdr << (ros_message.relay_status ? true : false);
  // Member: connect_status
  cdr << (ros_message.connect_status ? true : false);
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rei_robot_base
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  rei_robot_base::msg::CarData & ros_message)
{
  // Member: header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.header);

  // Member: motor_speed
  {
    cdr >> ros_message.motor_speed;
  }

  // Member: crash
  {
    cdr >> ros_message.crash;
  }

  // Member: cliff
  {
    cdr >> ros_message.cliff;
  }

  // Member: ultrasound
  {
    cdr >> ros_message.ultrasound;
  }

  // Member: smoke
  cdr >> ros_message.smoke;

  // Member: power_voltage
  cdr >> ros_message.power_voltage;

  // Member: is_charge
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.is_charge = tmp ? true : false;
  }

  // Member: tempareture
  cdr >> ros_message.tempareture;

  // Member: relative_humidity
  cdr >> ros_message.relative_humidity;

  // Member: input_io
  {
    cdr >> ros_message.input_io;
  }

  // Member: output_io
  {
    cdr >> ros_message.output_io;
  }

  // Member: relay_status
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.relay_status = tmp ? true : false;
  }

  // Member: connect_status
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.connect_status = tmp ? true : false;
  }

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rei_robot_base
get_serialized_size(
  const rei_robot_base::msg::CarData & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: header

  current_alignment +=
    std_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.header, current_alignment);
  // Member: motor_speed
  {
    size_t array_size = ros_message.motor_speed.size();

    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.motor_speed[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: crash
  {
    size_t array_size = ros_message.crash.size();

    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.crash[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: cliff
  {
    size_t array_size = ros_message.cliff.size();

    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.cliff[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: ultrasound
  {
    size_t array_size = ros_message.ultrasound.size();

    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.ultrasound[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: smoke
  {
    size_t item_size = sizeof(ros_message.smoke);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: power_voltage
  {
    size_t item_size = sizeof(ros_message.power_voltage);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: is_charge
  {
    size_t item_size = sizeof(ros_message.is_charge);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: tempareture
  {
    size_t item_size = sizeof(ros_message.tempareture);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: relative_humidity
  {
    size_t item_size = sizeof(ros_message.relative_humidity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: input_io
  {
    size_t array_size = 4;
    size_t item_size = sizeof(ros_message.input_io[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: output_io
  {
    size_t array_size = 7;
    size_t item_size = sizeof(ros_message.output_io[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: relay_status
  {
    size_t item_size = sizeof(ros_message.relay_status);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: connect_status
  {
    size_t item_size = sizeof(ros_message.connect_status);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rei_robot_base
max_serialized_size_CarData(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;


  // Member: header
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        std_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: motor_speed
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Member: crash
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: cliff
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: ultrasound
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: smoke
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: power_voltage
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: is_charge
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: tempareture
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: relative_humidity
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: input_io
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: output_io
  {
    size_t array_size = 7;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: relay_status
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: connect_status
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = rei_robot_base::msg::CarData;
    is_plain =
      (
      offsetof(DataType, connect_status) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _CarData__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const rei_robot_base::msg::CarData *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _CarData__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<rei_robot_base::msg::CarData *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _CarData__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const rei_robot_base::msg::CarData *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _CarData__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_CarData(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _CarData__callbacks = {
  "rei_robot_base::msg",
  "CarData",
  _CarData__cdr_serialize,
  _CarData__cdr_deserialize,
  _CarData__get_serialized_size,
  _CarData__max_serialized_size
};

static rosidl_message_type_support_t _CarData__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_CarData__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace rei_robot_base

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_rei_robot_base
const rosidl_message_type_support_t *
get_message_type_support_handle<rei_robot_base::msg::CarData>()
{
  return &rei_robot_base::msg::typesupport_fastrtps_cpp::_CarData__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, rei_robot_base, msg, CarData)() {
  return &rei_robot_base::msg::typesupport_fastrtps_cpp::_CarData__handle;
}

#ifdef __cplusplus
}
#endif
