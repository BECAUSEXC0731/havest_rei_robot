// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from arm_controller:srv/PickPlace.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__STRUCT_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__STRUCT_HPP_

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
# define DEPRECATED__arm_controller__srv__PickPlace_Request __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__PickPlace_Request __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct PickPlace_Request_
{
  using Type = PickPlace_Request_<ContainerAllocator>;

  explicit PickPlace_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->number = 0;
      this->mode = 0;
    }
  }

  explicit PickPlace_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->number = 0;
      this->mode = 0;
    }
  }

  // field types and members
  using _number_type =
    uint8_t;
  _number_type number;
  using _mode_type =
    uint8_t;
  _mode_type mode;
  using _pose_type =
    arm_controller::msg::Control_<ContainerAllocator>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__number(
    const uint8_t & _arg)
  {
    this->number = _arg;
    return *this;
  }
  Type & set__mode(
    const uint8_t & _arg)
  {
    this->mode = _arg;
    return *this;
  }
  Type & set__pose(
    const arm_controller::msg::Control_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    arm_controller::srv::PickPlace_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::PickPlace_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::PickPlace_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::PickPlace_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__PickPlace_Request
    std::shared_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__PickPlace_Request
    std::shared_ptr<arm_controller::srv::PickPlace_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PickPlace_Request_ & other) const
  {
    if (this->number != other.number) {
      return false;
    }
    if (this->mode != other.mode) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const PickPlace_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PickPlace_Request_

// alias to use template instance with default allocator
using PickPlace_Request =
  arm_controller::srv::PickPlace_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller


// Include directives for member types
// Member 'pose'
// already included above
// #include "arm_controller/msg/detail/control__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__PickPlace_Response __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__PickPlace_Response __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct PickPlace_Response_
{
  using Type = PickPlace_Response_<ContainerAllocator>;

  explicit PickPlace_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit PickPlace_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _pose_type =
    arm_controller::msg::Control_<ContainerAllocator>;
  _pose_type pose;
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__pose(
    const arm_controller::msg::Control_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }
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
    arm_controller::srv::PickPlace_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::PickPlace_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::PickPlace_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::PickPlace_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__PickPlace_Response
    std::shared_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__PickPlace_Response
    std::shared_ptr<arm_controller::srv::PickPlace_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PickPlace_Response_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const PickPlace_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PickPlace_Response_

// alias to use template instance with default allocator
using PickPlace_Response =
  arm_controller::srv::PickPlace_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller

namespace arm_controller
{

namespace srv
{

struct PickPlace
{
  using Request = arm_controller::srv::PickPlace_Request;
  using Response = arm_controller::srv::PickPlace_Response;
};

}  // namespace srv

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__PICK_PLACE__STRUCT_HPP_
