// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rei_robot_base:srv/SetIO.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__SET_IO__STRUCT_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__SET_IO__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__rei_robot_base__srv__SetIO_Request __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__srv__SetIO_Request __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetIO_Request_
{
  using Type = SetIO_Request_<ContainerAllocator>;

  explicit SetIO_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->all_off = false;
      this->all_on = false;
      this->state = false;
    }
  }

  explicit SetIO_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->all_off = false;
      this->all_on = false;
      this->state = false;
    }
  }

  // field types and members
  using _all_off_type =
    bool;
  _all_off_type all_off;
  using _all_on_type =
    bool;
  _all_on_type all_on;
  using _io_type =
    std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>>;
  _io_type io;
  using _state_type =
    bool;
  _state_type state;

  // setters for named parameter idiom
  Type & set__all_off(
    const bool & _arg)
  {
    this->all_off = _arg;
    return *this;
  }
  Type & set__all_on(
    const bool & _arg)
  {
    this->all_on = _arg;
    return *this;
  }
  Type & set__io(
    const std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>> & _arg)
  {
    this->io = _arg;
    return *this;
  }
  Type & set__state(
    const bool & _arg)
  {
    this->state = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::srv::SetIO_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::srv::SetIO_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::SetIO_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::SetIO_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__srv__SetIO_Request
    std::shared_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__srv__SetIO_Request
    std::shared_ptr<rei_robot_base::srv::SetIO_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetIO_Request_ & other) const
  {
    if (this->all_off != other.all_off) {
      return false;
    }
    if (this->all_on != other.all_on) {
      return false;
    }
    if (this->io != other.io) {
      return false;
    }
    if (this->state != other.state) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetIO_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetIO_Request_

// alias to use template instance with default allocator
using SetIO_Request =
  rei_robot_base::srv::SetIO_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rei_robot_base


#ifndef _WIN32
# define DEPRECATED__rei_robot_base__srv__SetIO_Response __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__srv__SetIO_Response __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetIO_Response_
{
  using Type = SetIO_Response_<ContainerAllocator>;

  explicit SetIO_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit SetIO_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    rei_robot_base::srv::SetIO_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::srv::SetIO_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::SetIO_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::SetIO_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__srv__SetIO_Response
    std::shared_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__srv__SetIO_Response
    std::shared_ptr<rei_robot_base::srv::SetIO_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetIO_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetIO_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetIO_Response_

// alias to use template instance with default allocator
using SetIO_Response =
  rei_robot_base::srv::SetIO_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rei_robot_base

namespace rei_robot_base
{

namespace srv
{

struct SetIO
{
  using Request = rei_robot_base::srv::SetIO_Request;
  using Response = rei_robot_base::srv::SetIO_Response;
};

}  // namespace srv

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__SRV__DETAIL__SET_IO__STRUCT_HPP_
