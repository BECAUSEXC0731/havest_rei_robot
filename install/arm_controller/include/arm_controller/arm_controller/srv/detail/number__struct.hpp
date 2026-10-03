// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROLLER__SRV__DETAIL__NUMBER__STRUCT_HPP_
#define ARM_CONTROLLER__SRV__DETAIL__NUMBER__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__Number_Request __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__Number_Request __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Number_Request_
{
  using Type = Number_Request_<ContainerAllocator>;

  explicit Number_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->data = 0;
    }
  }

  explicit Number_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    arm_controller::srv::Number_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::Number_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::Number_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::Number_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Number_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Number_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Number_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Number_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::Number_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::Number_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__Number_Request
    std::shared_ptr<arm_controller::srv::Number_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__Number_Request
    std::shared_ptr<arm_controller::srv::Number_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Number_Request_ & other) const
  {
    if (this->data != other.data) {
      return false;
    }
    return true;
  }
  bool operator!=(const Number_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Number_Request_

// alias to use template instance with default allocator
using Number_Request =
  arm_controller::srv::Number_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller


// Include directives for member types
// Member 'pose'
#include "arm_controller/msg/detail/control__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__arm_controller__srv__Number_Response __attribute__((deprecated))
#else
# define DEPRECATED__arm_controller__srv__Number_Response __declspec(deprecated)
#endif

namespace arm_controller
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Number_Response_
{
  using Type = Number_Response_<ContainerAllocator>;

  explicit Number_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  explicit Number_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
  using _number_type =
    std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>>;
  _number_type number;
  using _pose_type =
    std::vector<arm_controller::msg::Control_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<arm_controller::msg::Control_<ContainerAllocator>>>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__number(
    const std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>> & _arg)
  {
    this->number = _arg;
    return *this;
  }
  Type & set__pose(
    const std::vector<arm_controller::msg::Control_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<arm_controller::msg::Control_<ContainerAllocator>>> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    arm_controller::srv::Number_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const arm_controller::srv::Number_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<arm_controller::srv::Number_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<arm_controller::srv::Number_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Number_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Number_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      arm_controller::srv::Number_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<arm_controller::srv::Number_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<arm_controller::srv::Number_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<arm_controller::srv::Number_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__arm_controller__srv__Number_Response
    std::shared_ptr<arm_controller::srv::Number_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__arm_controller__srv__Number_Response
    std::shared_ptr<arm_controller::srv::Number_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Number_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->number != other.number) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const Number_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Number_Response_

// alias to use template instance with default allocator
using Number_Response =
  arm_controller::srv::Number_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace arm_controller

namespace arm_controller
{

namespace srv
{

struct Number
{
  using Request = arm_controller::srv::Number_Request;
  using Response = arm_controller::srv::Number_Response;
};

}  // namespace srv

}  // namespace arm_controller

#endif  // ARM_CONTROLLER__SRV__DETAIL__NUMBER__STRUCT_HPP_
