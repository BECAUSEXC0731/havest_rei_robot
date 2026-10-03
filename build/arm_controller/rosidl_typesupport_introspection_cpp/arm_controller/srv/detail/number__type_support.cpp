// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "arm_controller/srv/detail/number__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace arm_controller
{

namespace srv
{

namespace rosidl_typesupport_introspection_cpp
{

void Number_Request_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) arm_controller::srv::Number_Request(_init);
}

void Number_Request_fini_function(void * message_memory)
{
  auto typed_message = static_cast<arm_controller::srv::Number_Request *>(message_memory);
  typed_message->~Number_Request();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Number_Request_message_member_array[1] = {
  {
    "data",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller::srv::Number_Request, data),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Number_Request_message_members = {
  "arm_controller::srv",  // message namespace
  "Number_Request",  // message name
  1,  // number of fields
  sizeof(arm_controller::srv::Number_Request),
  Number_Request_message_member_array,  // message members
  Number_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  Number_Request_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Number_Request_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Number_Request_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace srv

}  // namespace arm_controller


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<arm_controller::srv::Number_Request>()
{
  return &::arm_controller::srv::rosidl_typesupport_introspection_cpp::Number_Request_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, arm_controller, srv, Number_Request)() {
  return &::arm_controller::srv::rosidl_typesupport_introspection_cpp::Number_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "arm_controller/srv/detail/number__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace arm_controller
{

namespace srv
{

namespace rosidl_typesupport_introspection_cpp
{

void Number_Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) arm_controller::srv::Number_Response(_init);
}

void Number_Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<arm_controller::srv::Number_Response *>(message_memory);
  typed_message->~Number_Response();
}

size_t size_function__Number_Response__number(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int8_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__Number_Response__number(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int8_t> *>(untyped_member);
  return &member[index];
}

void * get_function__Number_Response__number(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int8_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__Number_Response__number(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int8_t *>(
    get_const_function__Number_Response__number(untyped_member, index));
  auto & value = *reinterpret_cast<int8_t *>(untyped_value);
  value = item;
}

void assign_function__Number_Response__number(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int8_t *>(
    get_function__Number_Response__number(untyped_member, index));
  const auto & value = *reinterpret_cast<const int8_t *>(untyped_value);
  item = value;
}

void resize_function__Number_Response__number(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int8_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__Number_Response__pose(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<arm_controller::msg::Control> *>(untyped_member);
  return member->size();
}

const void * get_const_function__Number_Response__pose(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<arm_controller::msg::Control> *>(untyped_member);
  return &member[index];
}

void * get_function__Number_Response__pose(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<arm_controller::msg::Control> *>(untyped_member);
  return &member[index];
}

void fetch_function__Number_Response__pose(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const arm_controller::msg::Control *>(
    get_const_function__Number_Response__pose(untyped_member, index));
  auto & value = *reinterpret_cast<arm_controller::msg::Control *>(untyped_value);
  value = item;
}

void assign_function__Number_Response__pose(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<arm_controller::msg::Control *>(
    get_function__Number_Response__pose(untyped_member, index));
  const auto & value = *reinterpret_cast<const arm_controller::msg::Control *>(untyped_value);
  item = value;
}

void resize_function__Number_Response__pose(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<arm_controller::msg::Control> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Number_Response_message_member_array[3] = {
  {
    "success",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller::srv::Number_Response, success),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "number",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller::srv::Number_Response, number),  // bytes offset in struct
    nullptr,  // default value
    size_function__Number_Response__number,  // size() function pointer
    get_const_function__Number_Response__number,  // get_const(index) function pointer
    get_function__Number_Response__number,  // get(index) function pointer
    fetch_function__Number_Response__number,  // fetch(index, &value) function pointer
    assign_function__Number_Response__number,  // assign(index, value) function pointer
    resize_function__Number_Response__number  // resize(index) function pointer
  },
  {
    "pose",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<arm_controller::msg::Control>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(arm_controller::srv::Number_Response, pose),  // bytes offset in struct
    nullptr,  // default value
    size_function__Number_Response__pose,  // size() function pointer
    get_const_function__Number_Response__pose,  // get_const(index) function pointer
    get_function__Number_Response__pose,  // get(index) function pointer
    fetch_function__Number_Response__pose,  // fetch(index, &value) function pointer
    assign_function__Number_Response__pose,  // assign(index, value) function pointer
    resize_function__Number_Response__pose  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Number_Response_message_members = {
  "arm_controller::srv",  // message namespace
  "Number_Response",  // message name
  3,  // number of fields
  sizeof(arm_controller::srv::Number_Response),
  Number_Response_message_member_array,  // message members
  Number_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  Number_Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Number_Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Number_Response_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace srv

}  // namespace arm_controller


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<arm_controller::srv::Number_Response>()
{
  return &::arm_controller::srv::rosidl_typesupport_introspection_cpp::Number_Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, arm_controller, srv, Number_Response)() {
  return &::arm_controller::srv::rosidl_typesupport_introspection_cpp::Number_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"
// already included above
// #include "arm_controller/srv/detail/number__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/service_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/service_type_support_decl.hpp"

namespace arm_controller
{

namespace srv
{

namespace rosidl_typesupport_introspection_cpp
{

// this is intentionally not const to allow initialization later to prevent an initialization race
static ::rosidl_typesupport_introspection_cpp::ServiceMembers Number_service_members = {
  "arm_controller::srv",  // service namespace
  "Number",  // service name
  // these two fields are initialized below on the first access
  // see get_service_type_support_handle<arm_controller::srv::Number>()
  nullptr,  // request message
  nullptr  // response message
};

static const rosidl_service_type_support_t Number_service_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Number_service_members,
  get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace srv

}  // namespace arm_controller


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<arm_controller::srv::Number>()
{
  // get a handle to the value to be returned
  auto service_type_support =
    &::arm_controller::srv::rosidl_typesupport_introspection_cpp::Number_service_type_support_handle;
  // get a non-const and properly typed version of the data void *
  auto service_members = const_cast<::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
    static_cast<const ::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
      service_type_support->data));
  // make sure that both the request_members_ and the response_members_ are initialized
  // if they are not, initialize them
  if (
    service_members->request_members_ == nullptr ||
    service_members->response_members_ == nullptr)
  {
    // initialize the request_members_ with the static function from the external library
    service_members->request_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::arm_controller::srv::Number_Request
      >()->data
      );
    // initialize the response_members_ with the static function from the external library
    service_members->response_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::arm_controller::srv::Number_Response
      >()->data
      );
  }
  // finally return the properly initialized service_type_support handle
  return service_type_support;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, arm_controller, srv, Number)() {
  return ::rosidl_typesupport_introspection_cpp::get_service_type_support_handle<arm_controller::srv::Number>();
}

#ifdef __cplusplus
}
#endif
