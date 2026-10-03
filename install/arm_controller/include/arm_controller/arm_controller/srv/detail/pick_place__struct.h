// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from arm_controller:srv/PickPlace.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__STRUCT_H_
#define ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "arm_controller/msg/detail/control__struct.h"

/// Struct defined in srv/PickPlace in the package arm_controller.
typedef struct arm_controller__srv__PickPlace_Request
{
  uint8_t number;
  uint8_t mode;
  arm_controller__msg__Control pose;
} arm_controller__srv__PickPlace_Request;

// Struct for a sequence of arm_controller__srv__PickPlace_Request.
typedef struct arm_controller__srv__PickPlace_Request__Sequence
{
  arm_controller__srv__PickPlace_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_controller__srv__PickPlace_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'pose'
// already included above
// #include "arm_controller/msg/detail/control__struct.h"
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/PickPlace in the package arm_controller.
typedef struct arm_controller__srv__PickPlace_Response
{
  arm_controller__msg__Control pose;
  bool success;
  rosidl_runtime_c__String message;
} arm_controller__srv__PickPlace_Response;

// Struct for a sequence of arm_controller__srv__PickPlace_Response.
typedef struct arm_controller__srv__PickPlace_Response__Sequence
{
  arm_controller__srv__PickPlace_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} arm_controller__srv__PickPlace_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__STRUCT_H_
