// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__STRUCT_HPP_
#define REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__rei_robot_base__srv__CtrlMode_Request __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__srv__CtrlMode_Request __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CtrlMode_Request_
{
  using Type = CtrlMode_Request_<ContainerAllocator>;

  explicit CtrlMode_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->ctrl_mode = 0;
      this->use_acc = false;
    }
  }

  explicit CtrlMode_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->ctrl_mode = 0;
      this->use_acc = false;
    }
  }

  // field types and members
  using _ctrl_mode_type =
    int8_t;
  _ctrl_mode_type ctrl_mode;
  using _use_acc_type =
    bool;
  _use_acc_type use_acc;

  // setters for named parameter idiom
  Type & set__ctrl_mode(
    const int8_t & _arg)
  {
    this->ctrl_mode = _arg;
    return *this;
  }
  Type & set__use_acc(
    const bool & _arg)
  {
    this->use_acc = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__srv__CtrlMode_Request
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__srv__CtrlMode_Request
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CtrlMode_Request_ & other) const
  {
    if (this->ctrl_mode != other.ctrl_mode) {
      return false;
    }
    if (this->use_acc != other.use_acc) {
      return false;
    }
    return true;
  }
  bool operator!=(const CtrlMode_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CtrlMode_Request_

// alias to use template instance with default allocator
using CtrlMode_Request =
  rei_robot_base::srv::CtrlMode_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rei_robot_base


#ifndef _WIN32
# define DEPRECATED__rei_robot_base__srv__CtrlMode_Response __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__srv__CtrlMode_Response __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CtrlMode_Response_
{
  using Type = CtrlMode_Response_<ContainerAllocator>;

  explicit CtrlMode_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  explicit CtrlMode_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__srv__CtrlMode_Response
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__srv__CtrlMode_Response
    std::shared_ptr<rei_robot_base::srv::CtrlMode_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CtrlMode_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    return true;
  }
  bool operator!=(const CtrlMode_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CtrlMode_Response_

// alias to use template instance with default allocator
using CtrlMode_Response =
  rei_robot_base::srv::CtrlMode_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rei_robot_base

namespace rei_robot_base
{

namespace srv
{

struct CtrlMode
{
  using Request = rei_robot_base::srv::CtrlMode_Request;
  using Response = rei_robot_base::srv::CtrlMode_Response;
};

}  // namespace srv

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__SRV__DETAIL__CTRL_MODE__STRUCT_HPP_
