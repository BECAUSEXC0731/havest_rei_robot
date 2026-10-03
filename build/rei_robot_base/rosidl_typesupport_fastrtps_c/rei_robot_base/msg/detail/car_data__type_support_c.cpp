// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/msg/detail/car_data__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rei_robot_base/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rei_robot_base/msg/detail/car_data__struct.h"
#include "rei_robot_base/msg/detail/car_data__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosidl_runtime_c/primitives_sequence.h"  // cliff, crash, motor_speed, ultrasound
#include "rosidl_runtime_c/primitives_sequence_functions.h"  // cliff, crash, motor_speed, ultrasound
#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions
ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_rei_robot_base
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_rei_robot_base
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_rei_robot_base
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _CarData__ros_msg_type = rei_robot_base__msg__CarData;

static bool _CarData__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _CarData__ros_msg_type * ros_message = static_cast<const _CarData__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->header, cdr))
    {
      return false;
    }
  }

  // Field name: motor_speed
  {
    size_t size = ros_message->motor_speed.size;
    auto array_ptr = ros_message->motor_speed.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: crash
  {
    size_t size = ros_message->crash.size;
    auto array_ptr = ros_message->crash.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: cliff
  {
    size_t size = ros_message->cliff.size;
    auto array_ptr = ros_message->cliff.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: ultrasound
  {
    size_t size = ros_message->ultrasound.size;
    auto array_ptr = ros_message->ultrasound.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: smoke
  {
    cdr << ros_message->smoke;
  }

  // Field name: power_voltage
  {
    cdr << ros_message->power_voltage;
  }

  // Field name: is_charge
  {
    cdr << (ros_message->is_charge ? true : false);
  }

  // Field name: tempareture
  {
    cdr << ros_message->tempareture;
  }

  // Field name: relative_humidity
  {
    cdr << ros_message->relative_humidity;
  }

  // Field name: input_io
  {
    size_t size = 4;
    auto array_ptr = ros_message->input_io;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: output_io
  {
    size_t size = 7;
    auto array_ptr = ros_message->output_io;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: relay_status
  {
    cdr << (ros_message->relay_status ? true : false);
  }

  // Field name: connect_status
  {
    cdr << (ros_message->connect_status ? true : false);
  }

  return true;
}

static bool _CarData__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _CarData__ros_msg_type * ros_message = static_cast<_CarData__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->header))
    {
      return false;
    }
  }

  // Field name: motor_speed
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->motor_speed.data) {
      rosidl_runtime_c__double__Sequence__fini(&ros_message->motor_speed);
    }
    if (!rosidl_runtime_c__double__Sequence__init(&ros_message->motor_speed, size)) {
      fprintf(stderr, "failed to create array for field 'motor_speed'");
      return false;
    }
    auto array_ptr = ros_message->motor_speed.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: crash
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->crash.data) {
      rosidl_runtime_c__int8__Sequence__fini(&ros_message->crash);
    }
    if (!rosidl_runtime_c__int8__Sequence__init(&ros_message->crash, size)) {
      fprintf(stderr, "failed to create array for field 'crash'");
      return false;
    }
    auto array_ptr = ros_message->crash.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: cliff
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->cliff.data) {
      rosidl_runtime_c__int8__Sequence__fini(&ros_message->cliff);
    }
    if (!rosidl_runtime_c__int8__Sequence__init(&ros_message->cliff, size)) {
      fprintf(stderr, "failed to create array for field 'cliff'");
      return false;
    }
    auto array_ptr = ros_message->cliff.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: ultrasound
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->ultrasound.data) {
      rosidl_runtime_c__float__Sequence__fini(&ros_message->ultrasound);
    }
    if (!rosidl_runtime_c__float__Sequence__init(&ros_message->ultrasound, size)) {
      fprintf(stderr, "failed to create array for field 'ultrasound'");
      return false;
    }
    auto array_ptr = ros_message->ultrasound.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: smoke
  {
    cdr >> ros_message->smoke;
  }

  // Field name: power_voltage
  {
    cdr >> ros_message->power_voltage;
  }

  // Field name: is_charge
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->is_charge = tmp ? true : false;
  }

  // Field name: tempareture
  {
    cdr >> ros_message->tempareture;
  }

  // Field name: relative_humidity
  {
    cdr >> ros_message->relative_humidity;
  }

  // Field name: input_io
  {
    size_t size = 4;
    auto array_ptr = ros_message->input_io;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: output_io
  {
    size_t size = 7;
    auto array_ptr = ros_message->output_io;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: relay_status
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->relay_status = tmp ? true : false;
  }

  // Field name: connect_status
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->connect_status = tmp ? true : false;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rei_robot_base
size_t get_serialized_size_rei_robot_base__msg__CarData(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CarData__ros_msg_type * ros_message = static_cast<const _CarData__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name header

  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);
  // field.name motor_speed
  {
    size_t array_size = ros_message->motor_speed.size;
    auto array_ptr = ros_message->motor_speed.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name crash
  {
    size_t array_size = ros_message->crash.size;
    auto array_ptr = ros_message->crash.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name cliff
  {
    size_t array_size = ros_message->cliff.size;
    auto array_ptr = ros_message->cliff.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name ultrasound
  {
    size_t array_size = ros_message->ultrasound.size;
    auto array_ptr = ros_message->ultrasound.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name smoke
  {
    size_t item_size = sizeof(ros_message->smoke);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name power_voltage
  {
    size_t item_size = sizeof(ros_message->power_voltage);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name is_charge
  {
    size_t item_size = sizeof(ros_message->is_charge);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name tempareture
  {
    size_t item_size = sizeof(ros_message->tempareture);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name relative_humidity
  {
    size_t item_size = sizeof(ros_message->relative_humidity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name input_io
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->input_io;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name output_io
  {
    size_t array_size = 7;
    auto array_ptr = ros_message->output_io;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name relay_status
  {
    size_t item_size = sizeof(ros_message->relay_status);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name connect_status
  {
    size_t item_size = sizeof(ros_message->connect_status);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _CarData__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rei_robot_base__msg__CarData(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rei_robot_base
size_t max_serialized_size_rei_robot_base__msg__CarData(
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

  // member: header
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: motor_speed
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
  // member: crash
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: cliff
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: ultrasound
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
  // member: smoke
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: power_voltage
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: is_charge
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: tempareture
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: relative_humidity
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: input_io
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: output_io
  {
    size_t array_size = 7;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: relay_status
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: connect_status
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
    using DataType = rei_robot_base__msg__CarData;
    is_plain =
      (
      offsetof(DataType, connect_status) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _CarData__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_rei_robot_base__msg__CarData(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_CarData = {
  "rei_robot_base::msg",
  "CarData",
  _CarData__cdr_serialize,
  _CarData__cdr_deserialize,
  _CarData__get_serialized_size,
  _CarData__max_serialized_size
};

static rosidl_message_type_support_t _CarData__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_CarData,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, msg, CarData)() {
  return &_CarData__type_support;
}

#if defined(__cplusplus)
}
#endif
