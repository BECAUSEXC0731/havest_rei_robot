// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__STRUCT_H_
#define REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__STRUCT_H_

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
// Member 'motor_speed'
// Member 'crash'
// Member 'cliff'
// Member 'ultrasound'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/CarData in the package rei_robot_base.
typedef struct rei_robot_base__msg__CarData
{
  std_msgs__msg__Header header;
  rosidl_runtime_c__double__Sequence motor_speed;
  rosidl_runtime_c__int8__Sequence crash;
  rosidl_runtime_c__int8__Sequence cliff;
  rosidl_runtime_c__float__Sequence ultrasound;
  int8_t smoke;
  float power_voltage;
  bool is_charge;
  float tempareture;
  float relative_humidity;
  int8_t input_io[4];
  int8_t output_io[7];
  bool relay_status;
  bool connect_status;
} rei_robot_base__msg__CarData;

// Struct for a sequence of rei_robot_base__msg__CarData.
typedef struct rei_robot_base__msg__CarData__Sequence
{
  rei_robot_base__msg__CarData * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__msg__CarData__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__STRUCT_H_
