// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__STRUCT_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__STRUCT_HPP_

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
# define DEPRECATED__rei_robot_base__msg__CarData __attribute__((deprecated))
#else
# define DEPRECATED__rei_robot_base__msg__CarData __declspec(deprecated)
#endif

namespace rei_robot_base
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CarData_
{
  using Type = CarData_<ContainerAllocator>;

  explicit CarData_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->smoke = 0;
      this->power_voltage = 0.0f;
      this->is_charge = false;
      this->tempareture = 0.0f;
      this->relative_humidity = 0.0f;
      std::fill<typename std::array<int8_t, 4>::iterator, int8_t>(this->input_io.begin(), this->input_io.end(), 0);
      std::fill<typename std::array<int8_t, 7>::iterator, int8_t>(this->output_io.begin(), this->output_io.end(), 0);
      this->relay_status = false;
      this->connect_status = false;
    }
  }

  explicit CarData_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    input_io(_alloc),
    output_io(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->smoke = 0;
      this->power_voltage = 0.0f;
      this->is_charge = false;
      this->tempareture = 0.0f;
      this->relative_humidity = 0.0f;
      std::fill<typename std::array<int8_t, 4>::iterator, int8_t>(this->input_io.begin(), this->input_io.end(), 0);
      std::fill<typename std::array<int8_t, 7>::iterator, int8_t>(this->output_io.begin(), this->output_io.end(), 0);
      this->relay_status = false;
      this->connect_status = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _motor_speed_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _motor_speed_type motor_speed;
  using _crash_type =
    std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>>;
  _crash_type crash;
  using _cliff_type =
    std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>>;
  _cliff_type cliff;
  using _ultrasound_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _ultrasound_type ultrasound;
  using _smoke_type =
    int8_t;
  _smoke_type smoke;
  using _power_voltage_type =
    float;
  _power_voltage_type power_voltage;
  using _is_charge_type =
    bool;
  _is_charge_type is_charge;
  using _tempareture_type =
    float;
  _tempareture_type tempareture;
  using _relative_humidity_type =
    float;
  _relative_humidity_type relative_humidity;
  using _input_io_type =
    std::array<int8_t, 4>;
  _input_io_type input_io;
  using _output_io_type =
    std::array<int8_t, 7>;
  _output_io_type output_io;
  using _relay_status_type =
    bool;
  _relay_status_type relay_status;
  using _connect_status_type =
    bool;
  _connect_status_type connect_status;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__motor_speed(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->motor_speed = _arg;
    return *this;
  }
  Type & set__crash(
    const std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>> & _arg)
  {
    this->crash = _arg;
    return *this;
  }
  Type & set__cliff(
    const std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>> & _arg)
  {
    this->cliff = _arg;
    return *this;
  }
  Type & set__ultrasound(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->ultrasound = _arg;
    return *this;
  }
  Type & set__smoke(
    const int8_t & _arg)
  {
    this->smoke = _arg;
    return *this;
  }
  Type & set__power_voltage(
    const float & _arg)
  {
    this->power_voltage = _arg;
    return *this;
  }
  Type & set__is_charge(
    const bool & _arg)
  {
    this->is_charge = _arg;
    return *this;
  }
  Type & set__tempareture(
    const float & _arg)
  {
    this->tempareture = _arg;
    return *this;
  }
  Type & set__relative_humidity(
    const float & _arg)
  {
    this->relative_humidity = _arg;
    return *this;
  }
  Type & set__input_io(
    const std::array<int8_t, 4> & _arg)
  {
    this->input_io = _arg;
    return *this;
  }
  Type & set__output_io(
    const std::array<int8_t, 7> & _arg)
  {
    this->output_io = _arg;
    return *this;
  }
  Type & set__relay_status(
    const bool & _arg)
  {
    this->relay_status = _arg;
    return *this;
  }
  Type & set__connect_status(
    const bool & _arg)
  {
    this->connect_status = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rei_robot_base::msg::CarData_<ContainerAllocator> *;
  using ConstRawPtr =
    const rei_robot_base::msg::CarData_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rei_robot_base::msg::CarData_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rei_robot_base::msg::CarData_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::msg::CarData_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::msg::CarData_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rei_robot_base::msg::CarData_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rei_robot_base::msg::CarData_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rei_robot_base::msg::CarData_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rei_robot_base::msg::CarData_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rei_robot_base__msg__CarData
    std::shared_ptr<rei_robot_base::msg::CarData_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rei_robot_base__msg__CarData
    std::shared_ptr<rei_robot_base::msg::CarData_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CarData_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->motor_speed != other.motor_speed) {
      return false;
    }
    if (this->crash != other.crash) {
      return false;
    }
    if (this->cliff != other.cliff) {
      return false;
    }
    if (this->ultrasound != other.ultrasound) {
      return false;
    }
    if (this->smoke != other.smoke) {
      return false;
    }
    if (this->power_voltage != other.power_voltage) {
      return false;
    }
    if (this->is_charge != other.is_charge) {
      return false;
    }
    if (this->tempareture != other.tempareture) {
      return false;
    }
    if (this->relative_humidity != other.relative_humidity) {
      return false;
    }
    if (this->input_io != other.input_io) {
      return false;
    }
    if (this->output_io != other.output_io) {
      return false;
    }
    if (this->relay_status != other.relay_status) {
      return false;
    }
    if (this->connect_status != other.connect_status) {
      return false;
    }
    return true;
  }
  bool operator!=(const CarData_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CarData_

// alias to use template instance with default allocator
using CarData =
  rei_robot_base::msg::CarData_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__STRUCT_HPP_
