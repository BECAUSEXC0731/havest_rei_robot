// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rei_robot_base:msg/BumperCliff.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__STRUCT_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__STRUCT_HPP_

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
# define DEPRECATED__rei_robot_base__msg__BumperCliff __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__msg__BumperCliff __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct BumperCliff_
{
  using Type = BumperCliff_<ContainerAllocator>;

  explicit BumperCliff_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->bumper = false;
      this->cliff = false;
    }
  }

  explicit BumperCliff_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->bumper = false;
      this->cliff = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _bumper_type =
    bool;
  _bumper_type bumper;
  using _cliff_type =
    bool;
  _cliff_type cliff;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__bumper(
    const bool & _arg)
  {
    this->bumper = _arg;
    return *this;
  }
  Type & set__cliff(
    const bool & _arg)
  {
    this->cliff = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::msg::BumperCliff_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::msg::BumperCliff_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::msg::BumperCliff_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::msg::BumperCliff_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__msg__BumperCliff
    std::shared_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__msg__BumperCliff
    std::shared_ptr<rei_robot_base::msg::BumperCliff_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const BumperCliff_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->bumper != other.bumper) {
      return false;
    }
    if (this->cliff != other.cliff) {
      return false;
    }
    return true;
  }
  bool operator!=(const BumperCliff_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct BumperCliff_

// alias to use template instance with default allocator
using BumperCliff =
  rei_robot_base::msg::BumperCliff_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__STRUCT_HPP_
