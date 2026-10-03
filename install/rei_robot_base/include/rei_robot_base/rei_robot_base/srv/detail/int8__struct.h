// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rei_robot_base:srv/Int8.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__INT8__STRUCT_H_
#define REI_ROBOT_BASE__SRV__DETAIL__INT8__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/Int8 in the package rei_robot_base.
typedef struct rei_robot_base__srv__Int8_Request
{
  int8_t data;
} rei_robot_base__srv__Int8_Request;

// Struct for a sequence of rei_robot_base__srv__Int8_Request.
typedef struct rei_robot_base__srv__Int8_Request__Sequence
{
  rei_robot_base__srv__Int8_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__srv__Int8_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/Int8 in the package rei_robot_base.
typedef struct rei_robot_base__srv__Int8_Response
{
  bool success;
  rosidl_runtime_c__String message;
} rei_robot_base__srv__Int8_Response;

// Struct for a sequence of rei_robot_base__srv__Int8_Response.
typedef struct rei_robot_base__srv__Int8_Response__Sequence
{
  rei_robot_base__srv__Int8_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__srv__Int8_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // REI_ROBOT_BASE__SRV__DETAIL__INT8__STRUCT_H_
