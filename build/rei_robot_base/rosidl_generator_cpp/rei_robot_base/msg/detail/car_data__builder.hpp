// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__BUILDER_HPP_
#define REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rei_robot_base/msg/detail/car_data__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rei_robot_base
{

namespace msg
{

namespace builder
{

class Init_CarData_connect_status
{
public:
  explicit Init_CarData_connect_status(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  ::rei_robot_base::msg::CarData connect_status(::rei_robot_base::msg::CarData::_connect_status_type arg)
  {
    msg_.connect_status = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_relay_status
{
public:
  explicit Init_CarData_relay_status(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_connect_status relay_status(::rei_robot_base::msg::CarData::_relay_status_type arg)
  {
    msg_.relay_status = std::move(arg);
    return Init_CarData_connect_status(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_output_io
{
public:
  explicit Init_CarData_output_io(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_relay_status output_io(::rei_robot_base::msg::CarData::_output_io_type arg)
  {
    msg_.output_io = std::move(arg);
    return Init_CarData_relay_status(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_input_io
{
public:
  explicit Init_CarData_input_io(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_output_io input_io(::rei_robot_base::msg::CarData::_input_io_type arg)
  {
    msg_.input_io = std::move(arg);
    return Init_CarData_output_io(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_relative_humidity
{
public:
  explicit Init_CarData_relative_humidity(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_input_io relative_humidity(::rei_robot_base::msg::CarData::_relative_humidity_type arg)
  {
    msg_.relative_humidity = std::move(arg);
    return Init_CarData_input_io(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_tempareture
{
public:
  explicit Init_CarData_tempareture(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_relative_humidity tempareture(::rei_robot_base::msg::CarData::_tempareture_type arg)
  {
    msg_.tempareture = std::move(arg);
    return Init_CarData_relative_humidity(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_is_charge
{
public:
  explicit Init_CarData_is_charge(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_tempareture is_charge(::rei_robot_base::msg::CarData::_is_charge_type arg)
  {
    msg_.is_charge = std::move(arg);
    return Init_CarData_tempareture(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_power_voltage
{
public:
  explicit Init_CarData_power_voltage(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_is_charge power_voltage(::rei_robot_base::msg::CarData::_power_voltage_type arg)
  {
    msg_.power_voltage = std::move(arg);
    return Init_CarData_is_charge(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_smoke
{
public:
  explicit Init_CarData_smoke(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_power_voltage smoke(::rei_robot_base::msg::CarData::_smoke_type arg)
  {
    msg_.smoke = std::move(arg);
    return Init_CarData_power_voltage(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_ultrasound
{
public:
  explicit Init_CarData_ultrasound(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_smoke ultrasound(::rei_robot_base::msg::CarData::_ultrasound_type arg)
  {
    msg_.ultrasound = std::move(arg);
    return Init_CarData_smoke(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_cliff
{
public:
  explicit Init_CarData_cliff(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_ultrasound cliff(::rei_robot_base::msg::CarData::_cliff_type arg)
  {
    msg_.cliff = std::move(arg);
    return Init_CarData_ultrasound(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_crash
{
public:
  explicit Init_CarData_crash(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_cliff crash(::rei_robot_base::msg::CarData::_crash_type arg)
  {
    msg_.crash = std::move(arg);
    return Init_CarData_cliff(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_motor_speed
{
public:
  explicit Init_CarData_motor_speed(::rei_robot_base::msg::CarData & msg)
  : msg_(msg)
  {}
  Init_CarData_crash motor_speed(::rei_robot_base::msg::CarData::_motor_speed_type arg)
  {
    msg_.motor_speed = std::move(arg);
    return Init_CarData_crash(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

class Init_CarData_header
{
public:
  Init_CarData_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CarData_motor_speed header(::rei_robot_base::msg::CarData::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CarData_motor_speed(msg_);
  }

private:
  ::rei_robot_base::msg::CarData msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rei_robot_base::msg::CarData>()
{
  return rei_robot_base::msg::builder::Init_CarData_header();
}

}  // namespace rei_robot_base

#endif  // REI_ROBOT_BASE__MSG__DETAIL__CAR_DATA__BUILDER_HPP_
