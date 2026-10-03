// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rei_robot_base/msg/detail/car_data__rosidl_typesupport_introspection_c.h"
#include "rei_robot_base/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rei_robot_base/msg/detail/car_data__functions.h"
#include "rei_robot_base/msg/detail/car_data__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `motor_speed`
// Member `crash`
// Member `cliff`
// Member `ultrasound`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rei_robot_base__msg__CarData__init(message_memory);
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_fini_function(void * message_memory)
{
  rei_robot_base__msg__CarData__fini(message_memory);
}

size_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__motor_speed(
  const void * untyped_member)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return member->size;
}

const void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__motor_speed(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__motor_speed(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__motor_speed(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__motor_speed(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__motor_speed(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__motor_speed(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

bool rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__motor_speed(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  rosidl_runtime_c__double__Sequence__fini(member);
  return rosidl_runtime_c__double__Sequence__init(member, size);
}

size_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__crash(
  const void * untyped_member)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return member->size;
}

const void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__crash(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__crash(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__crash(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int8_t * item =
    ((const int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__crash(untyped_member, index));
  int8_t * value =
    (int8_t *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__crash(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int8_t * item =
    ((int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__crash(untyped_member, index));
  const int8_t * value =
    (const int8_t *)(untyped_value);
  *item = *value;
}

bool rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__crash(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  rosidl_runtime_c__int8__Sequence__fini(member);
  return rosidl_runtime_c__int8__Sequence__init(member, size);
}

size_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__cliff(
  const void * untyped_member)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return member->size;
}

const void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__cliff(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__cliff(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__cliff(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int8_t * item =
    ((const int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__cliff(untyped_member, index));
  int8_t * value =
    (int8_t *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__cliff(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int8_t * item =
    ((int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__cliff(untyped_member, index));
  const int8_t * value =
    (const int8_t *)(untyped_value);
  *item = *value;
}

bool rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__cliff(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  rosidl_runtime_c__int8__Sequence__fini(member);
  return rosidl_runtime_c__int8__Sequence__init(member, size);
}

size_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__ultrasound(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__ultrasound(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__ultrasound(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__ultrasound(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__ultrasound(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__ultrasound(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__ultrasound(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__ultrasound(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__input_io(
  const void * untyped_member)
{
  (void)untyped_member;
  return 4;
}

const void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__input_io(
  const void * untyped_member, size_t index)
{
  const int8_t * member =
    (const int8_t *)(untyped_member);
  return &member[index];
}

void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__input_io(
  void * untyped_member, size_t index)
{
  int8_t * member =
    (int8_t *)(untyped_member);
  return &member[index];
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__input_io(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int8_t * item =
    ((const int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__input_io(untyped_member, index));
  int8_t * value =
    (int8_t *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__input_io(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int8_t * item =
    ((int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__input_io(untyped_member, index));
  const int8_t * value =
    (const int8_t *)(untyped_value);
  *item = *value;
}

size_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__output_io(
  const void * untyped_member)
{
  (void)untyped_member;
  return 7;
}

const void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__output_io(
  const void * untyped_member, size_t index)
{
  const int8_t * member =
    (const int8_t *)(untyped_member);
  return &member[index];
}

void * rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__output_io(
  void * untyped_member, size_t index)
{
  int8_t * member =
    (int8_t *)(untyped_member);
  return &member[index];
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__output_io(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int8_t * item =
    ((const int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__output_io(untyped_member, index));
  int8_t * value =
    (int8_t *)(untyped_value);
  *value = *item;
}

void rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__output_io(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int8_t * item =
    ((int8_t *)
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__output_io(untyped_member, index));
  const int8_t * value =
    (const int8_t *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_member_array[14] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "motor_speed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, motor_speed),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__motor_speed,  // size() function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__motor_speed,  // get_const(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__motor_speed,  // get(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__motor_speed,  // fetch(index, &value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__motor_speed,  // assign(index, value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__motor_speed  // resize(index) function pointer
  },
  {
    "crash",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, crash),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__crash,  // size() function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__crash,  // get_const(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__crash,  // get(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__crash,  // fetch(index, &value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__crash,  // assign(index, value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__crash  // resize(index) function pointer
  },
  {
    "cliff",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, cliff),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__cliff,  // size() function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__cliff,  // get_const(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__cliff,  // get(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__cliff,  // fetch(index, &value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__cliff,  // assign(index, value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__cliff  // resize(index) function pointer
  },
  {
    "ultrasound",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, ultrasound),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__ultrasound,  // size() function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__ultrasound,  // get_const(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__ultrasound,  // get(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__ultrasound,  // fetch(index, &value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__ultrasound,  // assign(index, value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__resize_function__CarData__ultrasound  // resize(index) function pointer
  },
  {
    "smoke",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, smoke),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "power_voltage",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, power_voltage),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "is_charge",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, is_charge),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "tempareture",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, tempareture),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "relative_humidity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, relative_humidity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "input_io",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    4,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, input_io),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__input_io,  // size() function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__input_io,  // get_const(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__input_io,  // get(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__input_io,  // fetch(index, &value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__input_io,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "output_io",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    7,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, output_io),  // bytes offset in struct
    NULL,  // default value
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__size_function__CarData__output_io,  // size() function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_const_function__CarData__output_io,  // get_const(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__get_function__CarData__output_io,  // get(index) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__fetch_function__CarData__output_io,  // fetch(index, &value) function pointer
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__assign_function__CarData__output_io,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "relay_status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, relay_status),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "connect_status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rei_robot_base__msg__CarData, connect_status),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_members = {
  "rei_robot_base__msg",  // message namespace
  "CarData",  // message name
  14,  // number of fields
  sizeof(rei_robot_base__msg__CarData),
  rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_member_array,  // message members
  rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_init_function,  // function to initialize message memory (memory has to be allocated)
  rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_type_support_handle = {
  0,
  &rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rei_robot_base
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rei_robot_base, msg, CarData)() {
  rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_type_support_handle.typesupport_identifier) {
    rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rei_robot_base__msg__CarData__rosidl_typesupport_introspection_c__CarData_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
