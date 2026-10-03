// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rei_robot_base/srv/detail/ctrl_mode__struct.h"
#include "rei_robot_base/srv/detail/ctrl_mode__type_support.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace rei_robot_base
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _CtrlMode_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _CtrlMode_Request_type_support_ids_t;

static const _CtrlMode_Request_type_support_ids_t _CtrlMode_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _CtrlMode_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _CtrlMode_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _CtrlMode_Request_type_support_symbol_names_t _CtrlMode_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rei_robot_base, srv, CtrlMode_Request)),
  }
};

typedef struct _CtrlMode_Request_type_support_data_t
{
  void * data[2];
} _CtrlMode_Request_type_support_data_t;

static _CtrlMode_Request_type_support_data_t _CtrlMode_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _CtrlMode_Request_message_typesupport_map = {
  2,
  "rei_robot_base",
  &_CtrlMode_Request_message_typesupport_ids.typesupport_identifier[0],
  &_CtrlMode_Request_message_typesupport_symbol_names.symbol_name[0],
  &_CtrlMode_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t CtrlMode_Request_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_CtrlMode_Request_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace rei_robot_base

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, rei_robot_base, srv, CtrlMode_Request)() {
  return &::rei_robot_base::srv::rosidl_typesupport_c::CtrlMode_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rei_robot_base/srv/detail/ctrl_mode__struct.h"
// already included above
// #include "rei_robot_base/srv/detail/ctrl_mode__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace rei_robot_base
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _CtrlMode_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _CtrlMode_Response_type_support_ids_t;

static const _CtrlMode_Response_type_support_ids_t _CtrlMode_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _CtrlMode_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _CtrlMode_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _CtrlMode_Response_type_support_symbol_names_t _CtrlMode_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rei_robot_base, srv, CtrlMode_Response)),
  }
};

typedef struct _CtrlMode_Response_type_support_data_t
{
  void * data[2];
} _CtrlMode_Response_type_support_data_t;

static _CtrlMode_Response_type_support_data_t _CtrlMode_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _CtrlMode_Response_message_typesupport_map = {
  2,
  "rei_robot_base",
  &_CtrlMode_Response_message_typesupport_ids.typesupport_identifier[0],
  &_CtrlMode_Response_message_typesupport_symbol_names.symbol_name[0],
  &_CtrlMode_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t CtrlMode_Response_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_CtrlMode_Response_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace rei_robot_base

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, rei_robot_base, srv, CtrlMode_Response)() {
  return &::rei_robot_base::srv::rosidl_typesupport_c::CtrlMode_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rei_robot_base/srv/detail/ctrl_mode__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/service_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace rei_robot_base
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _CtrlMode_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _CtrlMode_type_support_ids_t;

static const _CtrlMode_type_support_ids_t _CtrlMode_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _CtrlMode_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _CtrlMode_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _CtrlMode_type_support_symbol_names_t _CtrlMode_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rei_robot_base, srv, CtrlMode)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rei_robot_base, srv, CtrlMode)),
  }
};

typedef struct _CtrlMode_type_support_data_t
{
  void * data[2];
} _CtrlMode_type_support_data_t;

static _CtrlMode_type_support_data_t _CtrlMode_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _CtrlMode_service_typesupport_map = {
  2,
  "rei_robot_base",
  &_CtrlMode_service_typesupport_ids.typesupport_identifier[0],
  &_CtrlMode_service_typesupport_symbol_names.symbol_name[0],
  &_CtrlMode_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t CtrlMode_service_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_CtrlMode_service_typesupport_map),
  rosidl_typesupport_c__get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace rei_robot_base

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_c, rei_robot_base, srv, CtrlMode)() {
  return &::rei_robot_base::srv::rosidl_typesupport_c::CtrlMode_service_type_support_handle;
}

#ifdef __cplusplus
}
#endif
