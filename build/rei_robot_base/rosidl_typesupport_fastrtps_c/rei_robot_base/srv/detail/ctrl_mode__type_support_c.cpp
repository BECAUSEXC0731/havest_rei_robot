// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/srv/detail/ctrl_mode__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rei_robot_base/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rei_robot_base/srv/detail/ctrl_mode__struct.h"
#include "rei_robot_base/srv/detail/ctrl_mode__functions.h"
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


// forward declare type support functions


using _CtrlMode_Request__ros_msg_type = rei_robot_base__srv__CtrlMode_Request;

static bool _CtrlMode_Request__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _CtrlMode_Request__ros_msg_type * ros_message = static_cast<const _CtrlMode_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: ctrl_mode
  {
    cdr << ros_message->ctrl_mode;
  }

  // Field name: use_acc
  {
    cdr << (ros_message->use_acc ? true : false);
  }

  return true;
}

static bool _CtrlMode_Request__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _CtrlMode_Request__ros_msg_type * ros_message = static_cast<_CtrlMode_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: ctrl_mode
  {
    cdr >> ros_message->ctrl_mode;
  }

  // Field name: use_acc
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->use_acc = tmp ? true : false;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rei_robot_base
size_t get_serialized_size_rei_robot_base__srv__CtrlMode_Request(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CtrlMode_Request__ros_msg_type * ros_message = static_cast<const _CtrlMode_Request__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name ctrl_mode
  {
    size_t item_size = sizeof(ros_message->ctrl_mode);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name use_acc
  {
    size_t item_size = sizeof(ros_message->use_acc);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _CtrlMode_Request__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rei_robot_base__srv__CtrlMode_Request(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rei_robot_base
size_t max_serialized_size_rei_robot_base__srv__CtrlMode_Request(
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

  // member: ctrl_mode
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: use_acc
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
    using DataType = rei_robot_base__srv__CtrlMode_Request;
    is_plain =
      (
      offsetof(DataType, use_acc) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _CtrlMode_Request__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_rei_robot_base__srv__CtrlMode_Request(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_CtrlMode_Request = {
  "rei_robot_base::srv",
  "CtrlMode_Request",
  _CtrlMode_Request__cdr_serialize,
  _CtrlMode_Request__cdr_deserialize,
  _CtrlMode_Request__get_serialized_size,
  _CtrlMode_Request__max_serialized_size
};

static rosidl_message_type_support_t _CtrlMode_Request__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_CtrlMode_Request,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode_Request)() {
  return &_CtrlMode_Request__type_support;
}

#if defined(__cplusplus)
}
#endif

// already included above
// #include <cassert>
// already included above
// #include <limits>
// already included above
// #include <string>
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
// already included above
// #include "rei_robot_base/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
// already included above
// #include "rei_robot_base/srv/detail/ctrl_mode__struct.h"
// already included above
// #include "rei_robot_base/srv/detail/ctrl_mode__functions.h"
// already included above
// #include "fastcdr/Cdr.h"

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


// forward declare type support functions


using _CtrlMode_Response__ros_msg_type = rei_robot_base__srv__CtrlMode_Response;

static bool _CtrlMode_Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _CtrlMode_Response__ros_msg_type * ros_message = static_cast<const _CtrlMode_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: success
  {
    cdr << (ros_message->success ? true : false);
  }

  return true;
}

static bool _CtrlMode_Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _CtrlMode_Response__ros_msg_type * ros_message = static_cast<_CtrlMode_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: success
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->success = tmp ? true : false;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rei_robot_base
size_t get_serialized_size_rei_robot_base__srv__CtrlMode_Response(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CtrlMode_Response__ros_msg_type * ros_message = static_cast<const _CtrlMode_Response__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name success
  {
    size_t item_size = sizeof(ros_message->success);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _CtrlMode_Response__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rei_robot_base__srv__CtrlMode_Response(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rei_robot_base
size_t max_serialized_size_rei_robot_base__srv__CtrlMode_Response(
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

  // member: success
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
    using DataType = rei_robot_base__srv__CtrlMode_Response;
    is_plain =
      (
      offsetof(DataType, success) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _CtrlMode_Response__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_rei_robot_base__srv__CtrlMode_Response(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_CtrlMode_Response = {
  "rei_robot_base::srv",
  "CtrlMode_Response",
  _CtrlMode_Response__cdr_serialize,
  _CtrlMode_Response__cdr_deserialize,
  _CtrlMode_Response__get_serialized_size,
  _CtrlMode_Response__max_serialized_size
};

static rosidl_message_type_support_t _CtrlMode_Response__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_CtrlMode_Response,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode_Response)() {
  return &_CtrlMode_Response__type_support;
}

#if defined(__cplusplus)
}
#endif

#include "rosidl_typesupport_fastrtps_cpp/service_type_support.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rei_robot_base/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rei_robot_base/srv/ctrl_mode.h"

#if defined(__cplusplus)
extern "C"
{
#endif

static service_type_support_callbacks_t CtrlMode__callbacks = {
  "rei_robot_base::srv",
  "CtrlMode",
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode_Request)(),
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode_Response)(),
};

static rosidl_service_type_support_t CtrlMode__handle = {
  rosidl_typesupport_fastrtps_c__identifier,
  &CtrlMode__callbacks,
  get_service_typesupport_handle_function,
};

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode)() {
  return &CtrlMode__handle;
}

#if defined(__cplusplus)
}
#endif
