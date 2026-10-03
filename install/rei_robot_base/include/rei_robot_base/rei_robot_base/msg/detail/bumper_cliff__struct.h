// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rei_robot_base:msg/BumperCliff.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__STRUCT_H_
#define REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/BumperCliff in the package rei_robot_base.
typedef struct rei_robot_base__msg__BumperCliff
{
  std_msgs__msg__Header header;
  bool bumper;
  bool cliff;
} rei_robot_base__msg__BumperCliff;

// Struct for a sequence of rei_robot_base__msg__BumperCliff.
typedef struct rei_robot_base__msg__BumperCliff__Sequence
{
  rei_robot_base__msg__BumperCliff * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__msg__BumperCliff__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__STRUCT_H_
