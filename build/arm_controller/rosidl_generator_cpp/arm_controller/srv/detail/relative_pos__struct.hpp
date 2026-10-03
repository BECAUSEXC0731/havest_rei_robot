// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from arm_controller:srv/RelativePos.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__STRUCT_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__RelativePos_Request __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__RelativePos_Request __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RelativePos_Request_
{
  using Type = RelativePos_Request_<ContainerAllocator>;

  explicit RelativePos_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->dx = 0.0f;
      this->dy = 0.0f;
      this->dz = 0.0f;
    }
  }

  explicit RelativePos_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->dx = 0.0f;
      this->dy = 0.0f;
      this->dz = 0.0f;
    }
  }

  // field types and members
  using _dx_type =
    float;
  _dx_type dx;
  using _dy_type =
    float;
  _dy_type dy;
  using _dz_type =
    float;
  _dz_type dz;

  // setters for named parameter idiom
  Type & set__dx(
    const float & _arg)
  {
    this->dx = _arg;
    return *this;
  }
  Type & set__dy(
    const float & _arg)
  {
    this->dy = _arg;
    return *this;
  }
  Type & set__dz(
    const float & _arg)
  {
    this->dz = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    arm_controller::srv::RelativePos_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::RelativePos_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::RelativePos_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::RelativePos_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__RelativePos_Request
    std::shared_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__RelativePos_Request
    std::shared_ptr<arm_controller::srv::RelativePos_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RelativePos_Request_ & other) const
  {
    if (this->dx != other.dx) {
      return false;
    }
    if (this->dy != other.dy) {
      return false;
    }
    if (this->dz != other.dz) {
      return false;
    }
    return true;
  }
  bool operator!=(const RelativePos_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RelativePos_Request_

// alias to use template instance with default allocator
using RelativePos_Request =
  arm_controller::srv::RelativePos_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller


#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__RelativePos_Response __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__RelativePos_Response __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RelativePos_Response_
{
  using Type = RelativePos_Response_<ContainerAllocator>;

  explicit RelativePos_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit RelativePos_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    arm_controller::srv::RelativePos_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::RelativePos_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::RelativePos_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::RelativePos_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__RelativePos_Response
    std::shared_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__RelativePos_Response
    std::shared_ptr<arm_controller::srv::RelativePos_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RelativePos_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const RelativePos_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RelativePos_Response_

// alias to use template instance with default allocator
using RelativePos_Response =
  arm_controller::srv::RelativePos_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller

namespace arm_controller
{

namespace srv
{

struct RelativePos
{
  using Request = arm_controller::srv::RelativePos_Request;
  using Response = arm_controller::srv::RelativePos_Response;
};

}  // namespace srv

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__RELATIVE_POS__STRUCT_HPP_
