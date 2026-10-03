// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__STRUCT_H_
#define REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/CtrlMode in the package rei_robot_base.
typedef struct rei_robot_base__srv__CtrlMode_Request
{
  /// 0: velocity, 1: motor speed
  int8_t ctrl_mode;
  /// only valid when ctrl_mode is velocity
  bool use_acc;
} rei_robot_base__srv__CtrlMode_Request;

// Struct for a sequence of rei_robot_base__srv__CtrlMode_Request.
typedef struct rei_robot_base__srv__CtrlMode_Request__Sequence
{
  rei_robot_base__srv__CtrlMode_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__srv__CtrlMode_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/CtrlMode in the package rei_robot_base.
typedef struct rei_robot_base__srv__CtrlMode_Response
{
  bool success;
} rei_robot_base__srv__CtrlMode_Response;

// Struct for a sequence of rei_robot_base__srv__CtrlMode_Response.
typedef struct rei_robot_base__srv__CtrlMode_Response__Sequence
{
  rei_robot_base__srv__CtrlMode_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rei_robot_base__srv__CtrlMode_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__STRUCT_H_
