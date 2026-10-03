// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from arm_controller:msg/Control.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__MSG__DETAIL__CONTROL__STRUCT_H_
#define ARM_CONTROLLER__MSG__DETAIL__CONTROL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/Control in the package arm_controller.
typedef struct arm_controller__msg__Control
{
  geometry_msgs__msg__Point position;
  double roll;
  double pitch;
  double yaw;
} arm_controller__msg__Control;

// Struct for a sequence of arm_controller__msg__Control.
typedef struct arm_controller__msg__Control__Sequence
{
  arm_controller__msg__Control * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_controller__msg__Control__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ARM_CONTROLLER__MSG__DETAIL__CONTROL__STRUCT_H_
