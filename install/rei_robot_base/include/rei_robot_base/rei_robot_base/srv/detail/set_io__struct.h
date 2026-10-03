// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rei_robot_base:srv/SetIO.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__SET_IO__STRUCT_H_
#define REI_ROBOT_BASE__SRV__DETAIL__SET_IO__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'io'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in srv/SetIO in the package rei_robot_base.
typedef struct rei_robot_base__srv__SetIO_Request
{
  bool all_off;
  bool all_on;
  rosidl_runtime_c__int8__Sequence io;
  bool state;
} rei_robot_base__srv__SetIO_Request;

// Struct for a sequence of rei_robot_base__srv__SetIO_Request.
typedef struct rei_robot_base__srv__SetIO_Request__Sequence
{
  rei_robot_base__srv__SetIO_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__srv__SetIO_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/SetIO in the package rei_robot_base.
typedef struct rei_robot_base__srv__SetIO_Response
{
  bool success;
  rosidl_runtime_c__String message;
} rei_robot_base__srv__SetIO_Response;

// Struct for a sequence of rei_robot_base__srv__SetIO_Response.
typedef struct rei_robot_base__srv__SetIO_Response__Sequence
{
  rei_robot_base__srv__SetIO_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__srv__SetIO_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // REI_ROBOT_BASE__SRV__DETAIL__SET_IO__STRUCT_H_
