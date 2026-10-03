// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rei_robot_base:srv/Int8.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__INT8__STRUCT_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__INT8__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__rei_robot_base__srv__Int8_Request __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__srv__Int8_Request __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Int8_Request_
{
  using Type = Int8_Request_<ContainerAllocator>;

  explicit Int8_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->data = 0;
    }
  }

  explicit Int8_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->data = 0;
    }
  }

  // field types and members
  using _data_type =
    int8_t;
  _data_type data;

  // setters for named parameter idiom
  Type & set__data(
    const int8_t & _arg)
  {
    this->data = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::srv::Int8_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::srv::Int8_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::Int8_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::Int8_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__srv__Int8_Request
    std::shared_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__srv__Int8_Request
    std::shared_ptr<rei_robot_base::srv::Int8_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Int8_Request_ & other) const
  {
    if (this->data != other.data) {
      return false;
    }
    return true;
  }
  bool operator!=(const Int8_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Int8_Request_

// alias to use template instance with default allocator
using Int8_Request =
  rei_robot_base::srv::Int8_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rei_robot_base


#ifndef _WIN32
# define DEPRECATED__rei_robot_base__srv__Int8_Response __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__srv__Int8_Response __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Int8_Response_
{
  using Type = Int8_Response_<ContainerAllocator>;

  explicit Int8_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit Int8_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::srv::Int8_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::srv::Int8_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::Int8_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::Int8_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__srv__Int8_Response
    std::shared_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__srv__Int8_Response
    std::shared_ptr<rei_robot_base::srv::Int8_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Int8_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const Int8_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Int8_Response_

// alias to use template instance with default allocator
using Int8_Response =
  rei_robot_base::srv::Int8_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rei_robot_base

namespace rei_robot_base
{

namespace srv
{

struct Int8
{
  using Request = rei_robot_base::srv::Int8_Request;
  using Response = rei_robot_base::srv::Int8_Response;
};

}  // namespace srv

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__SRV__DETAIL__INT8__STRUCT_HPP_
