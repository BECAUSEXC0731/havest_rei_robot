// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from arm_controller:srv/Move.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__MOVE__STRUCT_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__MOVE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pose'
#include "arm_controller/msg/detail/control__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__Move_Request __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__Move_Request __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Move_Request_
{
  using Type = Move_Request_<ContainerAllocator>;

  explicit Move_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    (void)_init;
  }

  explicit Move_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _pose_type =
    arm_controller::msg::Control_<ContainerAllocator>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__pose(
    const arm_controller::msg::Control_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    arm_controller::srv::Move_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::Move_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::Move_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::Move_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Move_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Move_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Move_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Move_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::Move_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::Move_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__Move_Request
    std::shared_ptr<arm_controller::srv::Move_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__Move_Request
    std::shared_ptr<arm_controller::srv::Move_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Move_Request_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const Move_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Move_Request_

// alias to use template instance with default allocator
using Move_Request =
  arm_controller::srv::Move_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller


#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__Move_Response __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__Move_Response __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Move_Response_
{
  using Type = Move_Response_<ContainerAllocator>;

  explicit Move_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->message = "";
      this->success = false;
    }
  }

  explicit Move_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->message = "";
      this->success = false;
    }
  }

  // field types and members
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;
  using _success_type =
    bool;
  _success_type success;

  // setters for named parameter idiom
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    arm_controller::srv::Move_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::Move_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::Move_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::Move_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Move_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Move_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Move_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Move_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::Move_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::Move_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__Move_Response
    std::shared_ptr<arm_controller::srv::Move_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__Move_Response
    std::shared_ptr<arm_controller::srv::Move_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Move_Response_ & other) const
  {
    if (this->message != other.message) {
      return false;
    }
    if (this->success != other.success) {
      return false;
    }
    return true;
  }
  bool operator!=(const Move_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Move_Response_

// alias to use template instance with default allocator
using Move_Response =
  arm_controller::srv::Move_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller

namespace arm_controller
{

namespace srv
{

struct Move
{
  using Request = arm_controller::srv::Move_Request;
  using Response = arm_controller::srv::Move_Response;
};

}  // namespace srv

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__MOVE__STRUCT_HPP_
