// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "arm_controller/srv/detail/number__rosidl_typesupport_introspection_c.h"
#include "arm_controller/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "arm_controller/srv/detail/number__functions.h"
#include "arm_controller/srv/detail/number__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  arm_controller__srv__Number_Request__init(message_memory);
}

void arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_fini_function(void * message_memory)
{
  arm_controller__srv__Number_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_member_array[1] = {
  {
    "data",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller__srv__Number_Request, data),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_members = {
  "arm_controller__srv",  // message namespace
  "Number_Request",  // message name
  1,  // number of fields
  sizeof(arm_controller__srv__Number_Request),
  arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_member_array,  // message members
  arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_type_support_handle = {
  0,
  &arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_arm_controller
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number_Request)() {
  if (!arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_type_support_handle.typesupport_identifier) {
    arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &arm_controller__srv__Number_Request__rosidl_typesupport_introspection_c__Number_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "arm_controller/srv/detail/number__rosidl_typesupport_introspection_c.h"
// already included above
// #include "arm_controller/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "arm_controller/srv/detail/number__functions.h"
// already included above
// #include "arm_controller/srv/detail/number__struct.h"


// Include directives for member types
// Member `number`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `pose`
#include "arm_controller/msg/control.h"
// Member `pose`
#include "arm_controller/msg/detail/control__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  arm_controller__srv__Number_Response__init(message_memory);
}

void arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_fini_function(void * message_memory)
{
  arm_controller__srv__Number_Response__fini(message_memory);
}

size_t arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__size_function__Number_Response__number(
  const void * untyped_member)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return member->size;
}

const void * arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_const_function__Number_Response__number(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_function__Number_Response__number(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__fetch_function__Number_Response__number(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int8_t * item =
    ((const int8_t *)
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_const_function__Number_Response__number(untyped_member, index));
  int8_t * value =
    (int8_t *)(untyped_value);
  *value = *item;
}

void arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__assign_function__Number_Response__number(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int8_t * item =
    ((int8_t *)
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_function__Number_Response__number(untyped_member, index));
  const int8_t * value =
    (const int8_t *)(untyped_value);
  *item = *value;
}

bool arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__resize_function__Number_Response__number(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  rosidl_runtime_c__int8__Sequence__fini(member);
  return rosidl_runtime_c__int8__Sequence__init(member, size);
}

size_t arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__size_function__Number_Response__pose(
  const void * untyped_member)
{
  const arm_controller__msg__Control__Sequence * member =
    (const arm_controller__msg__Control__Sequence *)(untyped_member);
  return member->size;
}

const void * arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_const_function__Number_Response__pose(
  const void * untyped_member, size_t index)
{
  const arm_controller__msg__Control__Sequence * member =
    (const arm_controller__msg__Control__Sequence *)(untyped_member);
  return &member->data[index];
}

void * arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_function__Number_Response__pose(
  void * untyped_member, size_t index)
{
  arm_controller__msg__Control__Sequence * member =
    (arm_controller__msg__Control__Sequence *)(untyped_member);
  return &member->data[index];
}

void arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__fetch_function__Number_Response__pose(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const arm_controller__msg__Control * item =
    ((const arm_controller__msg__Control *)
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_const_function__Number_Response__pose(untyped_member, index));
  arm_controller__msg__Control * value =
    (arm_controller__msg__Control *)(untyped_value);
  *value = *item;
}

void arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__assign_function__Number_Response__pose(
  void * untyped_member, size_t index, const void * untyped_value)
{
  arm_controller__msg__Control * item =
    ((arm_controller__msg__Control *)
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_function__Number_Response__pose(untyped_member, index));
  const arm_controller__msg__Control * value =
    (const arm_controller__msg__Control *)(untyped_value);
  *item = *value;
}

bool arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__resize_function__Number_Response__pose(
  void * untyped_member, size_t size)
{
  arm_controller__msg__Control__Sequence * member =
    (arm_controller__msg__Control__Sequence *)(untyped_member);
  arm_controller__msg__Control__Sequence__fini(member);
  return arm_controller__msg__Control__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_member_array[3] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller__srv__Number_Response, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "number",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller__srv__Number_Response, number),  // bytes offset in struct
    NULL,  // default value
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__size_function__Number_Response__number,  // size() function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_const_function__Number_Response__number,  // get_const(index) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_function__Number_Response__number,  // get(index) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__fetch_function__Number_Response__number,  // fetch(index, &value) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__assign_function__Number_Response__number,  // assign(index, value) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__resize_function__Number_Response__number  // resize(index) function pointer
  },
  {
    "pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller__srv__Number_Response, pose),  // bytes offset in struct
    NULL,  // default value
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__size_function__Number_Response__pose,  // size() function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_const_function__Number_Response__pose,  // get_const(index) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__get_function__Number_Response__pose,  // get(index) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__fetch_function__Number_Response__pose,  // fetch(index, &value) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__assign_function__Number_Response__pose,  // assign(index, value) function pointer
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__resize_function__Number_Response__pose  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_members = {
  "arm_controller__srv",  // message namespace
  "Number_Response",  // message name
  3,  // number of fields
  sizeof(arm_controller__srv__Number_Response),
  arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_member_array,  // message members
  arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_type_support_handle = {
  0,
  &arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_arm_controller
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number_Response)() {
  arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, msg, Control)();
  if (!arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_type_support_handle.typesupport_identifier) {
    arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &arm_controller__srv__Number_Response__rosidl_typesupport_introspection_c__Number_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "arm_controller/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "arm_controller/srv/detail/number__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_members = {
  "arm_controller__srv",  // service namespace
  "Number",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_Request_message_type_support_handle,
  NULL  // response message
  // arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_Response_message_type_support_handle
};

static rosidl_service_type_support_t arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_type_support_handle = {
  0,
  &arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_arm_controller
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number)() {
  if (!arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_type_support_handle.typesupport_identifier) {
    arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, arm_controller, srv, Number_Response)()->data;
  }

  return &arm_controller__srv__detail__number__rosidl_typesupport_introspection_c__Number_service_type_support_handle;
}
