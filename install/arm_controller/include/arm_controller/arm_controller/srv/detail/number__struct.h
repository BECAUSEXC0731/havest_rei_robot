// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__NUMBER__STRUCT_H_
#define ARM_CONTROLLER__SRV__DETAIL__NUMBER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/Number in the package arm_controller.
typedef struct arm_controller__srv__Number_Request
{
  int8_t data;
} arm_controller__srv__Number_Request;

// Struct for a sequence of arm_controller__srv__Number_Request.
typedef struct arm_controller__srv__Number_Request__Sequence
{
  arm_controller__srv__Number_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_controller__srv__Number_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'number'
#include "rosidl_runtime_c/primitives_sequence.h"
// Member 'pose'
#include "arm_controller/msg/detail/control__struct.h"

/// Struct defined in srv/Number in the package arm_controller.
typedef struct arm_controller__srv__Number_Response
{
  bool success;
  rosidl_runtime_c__int8__Sequence number;
  arm_controller__msg__Control__Sequence pose;
} arm_controller__srv__Number_Response;

// Struct for a sequence of arm_controller__srv__Number_Response.
typedef struct arm_controller__srv__Number_Response__Sequence
{
  arm_controller__srv__Number_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_controller__srv__Number_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ARM_CONTROLLER__SRV__DETAIL__NUMBER__STRUCT_H_
