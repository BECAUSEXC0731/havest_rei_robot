// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rei_robot_base:msg/MotorCmd.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rei_robot_base/msg/detail/motor_cmd__rosidl_typesupport_introspection_c.h"
#include "rei_robot_base/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rei_robot_base/msg/detail/motor_cmd__functions.h"
#include "rei_robot_base/msg/detail/motor_cmd__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `motor_expect_speed`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rei_robot_base__msg__MotorCmd__init(message_memory);
}

void rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_fini_function(void * message_memory)
{
  rei_robot_base__msg__MotorCmd__fini(message_memory);
}

size_t rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__size_function__MotorCmd__motor_expect_speed(
  const void * untyped_member)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return member->size;
}

const void * rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__get_const_function__MotorCmd__motor_expect_speed(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__get_function__MotorCmd__motor_expect_speed(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__fetch_function__MotorCmd__motor_expect_speed(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__get_const_function__MotorCmd__motor_expect_speed(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__assign_function__MotorCmd__motor_expect_speed(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__get_function__MotorCmd__motor_expect_speed(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

bool rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__resize_function__MotorCmd__motor_expect_speed(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  rosidl_runtime_c__double__Sequence__fini(member);
  return rosidl_runtime_c__double__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__MotorCmd, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "motor_expect_speed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__MotorCmd, motor_expect_speed),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__size_function__MotorCmd__motor_expect_speed,  // size() function pointer
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__get_const_function__MotorCmd__motor_expect_speed,  // get_const(index) function pointer
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__get_function__MotorCmd__motor_expect_speed,  // get(index) function pointer
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__fetch_function__MotorCmd__motor_expect_speed,  // fetch(index, &value) function pointer
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__assign_function__MotorCmd__motor_expect_speed,  // assign(index, value) function pointer
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__resize_function__MotorCmd__motor_expect_speed  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_members = {
  "rei_robot_base__msg",  // message namespace
  "MotorCmd",  // message name
  2,  // number of fields
  sizeof(rei_robot_base__msg__MotorCmd),
  rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_member_array,  // message members
  rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_init_function,  // function to initialize message memory (memory has to be allocated)
  rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_type_support_handle = {
  0,
  &rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rei_robot_base
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rei_robot_base, msg, MotorCmd)() {
  rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_type_support_handle.typesupport_identifier) {
    rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rei_robot_base__msg__MotorCmd__rosidl_typesupport_introspection_c__MotorCmd_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
