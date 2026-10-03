// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rei_robot_base:msg/MotorCmd.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__STRUCT_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__rei_robot_base__msg__MotorCmd __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__msg__MotorCmd __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MotorCmd_
{
  using Type = MotorCmd_<ContainerAllocator>;

  explicit MotorCmd_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    (void)_init;
  }

  explicit MotorCmd_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _motor_expect_speed_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _motor_expect_speed_type motor_expect_speed;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__motor_expect_speed(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->motor_expect_speed = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::msg::MotorCmd_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::msg::MotorCmd_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::msg::MotorCmd_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::msg::MotorCmd_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__msg__MotorCmd
    std::shared_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__msg__MotorCmd
    std::shared_ptr<rei_robot_base::msg::MotorCmd_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MotorCmd_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->motor_expect_speed != other.motor_expect_speed) {
      return false;
    }
    return true;
  }
  bool operator!=(const MotorCmd_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MotorCmd_

// alias to use template instance with default allocator
using MotorCmd =
  rei_robot_base::msg::MotorCmd_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__MSG__DETAIL__MOTOR_CMD__STRUCT_HPP_
