// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rei_robot_base:msg/CarData.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/msg/detail/car_data__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `motor_speed`
// Member `crash`
// Member `cliff`
// Member `ultrasound`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
rei_robot_base__msg__CarData__init(rei_robot_base__msg__CarData * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    rei_robot_base__msg__CarData__fini(msg);
    return false;
  }
  // motor_speed
  if (!rosidl_runtime_c__double__Sequence__init(&msg->motor_speed, 0)) {
    rei_robot_base__msg__CarData__fini(msg);
    return false;
  }
  // crash
  if (!rosidl_runtime_c__int8__Sequence__init(&msg->crash, 0)) {
    rei_robot_base__msg__CarData__fini(msg);
    return false;
  }
  // cliff
  if (!rosidl_runtime_c__int8__Sequence__init(&msg->cliff, 0)) {
    rei_robot_base__msg__CarData__fini(msg);
    return false;
  }
  // ultrasound
  if (!rosidl_runtime_c__float__Sequence__init(&msg->ultrasound, 0)) {
    rei_robot_base__msg__CarData__fini(msg);
    return false;
  }
  // smoke
  // power_voltage
  // is_charge
  // tempareture
  // relative_humidity
  // input_io
  // output_io
  // relay_status
  // connect_status
  return true;
}

void
rei_robot_base__msg__CarData__fini(rei_robot_base__msg__CarData * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // motor_speed
  rosidl_runtime_c__double__Sequence__fini(&msg->motor_speed);
  // crash
  rosidl_runtime_c__int8__Sequence__fini(&msg->crash);
  // cliff
  rosidl_runtime_c__int8__Sequence__fini(&msg->cliff);
  // ultrasound
  rosidl_runtime_c__float__Sequence__fini(&msg->ultrasound);
  // smoke
  // power_voltage
  // is_charge
  // tempareture
  // relative_humidity
  // input_io
  // output_io
  // relay_status
  // connect_status
}

bool
rei_robot_base__msg__CarData__are_equal(const rei_robot_base__msg__CarData * lhs, const rei_robot_base__msg__CarData * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // motor_speed
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->motor_speed), &(rhs->motor_speed)))
  {
    return false;
  }
  // crash
  if (!rosidl_runtime_c__int8__Sequence__are_equal(
      &(lhs->crash), &(rhs->crash)))
  {
    return false;
  }
  // cliff
  if (!rosidl_runtime_c__int8__Sequence__are_equal(
      &(lhs->cliff), &(rhs->cliff)))
  {
    return false;
  }
  // ultrasound
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->ultrasound), &(rhs->ultrasound)))
  {
    return false;
  }
  // smoke
  if (lhs->smoke != rhs->smoke) {
    return false;
  }
  // power_voltage
  if (lhs->power_voltage != rhs->power_voltage) {
    return false;
  }
  // is_charge
  if (lhs->is_charge != rhs->is_charge) {
    return false;
  }
  // tempareture
  if (lhs->tempareture != rhs->tempareture) {
    return false;
  }
  // relative_humidity
  if (lhs->relative_humidity != rhs->relative_humidity) {
    return false;
  }
  // input_io
  for (size_t i = 0; i < 4; ++i) {
    if (lhs->input_io[i] != rhs->input_io[i]) {
      return false;
    }
  }
  // output_io
  for (size_t i = 0; i < 7; ++i) {
    if (lhs->output_io[i] != rhs->output_io[i]) {
      return false;
    }
  }
  // relay_status
  if (lhs->relay_status != rhs->relay_status) {
    return false;
  }
  // connect_status
  if (lhs->connect_status != rhs->connect_status) {
    return false;
  }
  return true;
}

bool
rei_robot_base__msg__CarData__copy(
  const rei_robot_base__msg__CarData * input,
  rei_robot_base__msg__CarData * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // motor_speed
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->motor_speed), &(output->motor_speed)))
  {
    return false;
  }
  // crash
  if (!rosidl_runtime_c__int8__Sequence__copy(
      &(input->crash), &(output->crash)))
  {
    return false;
  }
  // cliff
  if (!rosidl_runtime_c__int8__Sequence__copy(
      &(input->cliff), &(output->cliff)))
  {
    return false;
  }
  // ultrasound
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->ultrasound), &(output->ultrasound)))
  {
    return false;
  }
  // smoke
  output->smoke = input->smoke;
  // power_voltage
  output->power_voltage = input->power_voltage;
  // is_charge
  output->is_charge = input->is_charge;
  // tempareture
  output->tempareture = input->tempareture;
  // relative_humidity
  output->relative_humidity = input->relative_humidity;
  // input_io
  for (size_t i = 0; i < 4; ++i) {
    output->input_io[i] = input->input_io[i];
  }
  // output_io
  for (size_t i = 0; i < 7; ++i) {
    output->output_io[i] = input->output_io[i];
  }
  // relay_status
  output->relay_status = input->relay_status;
  // connect_status
  output->connect_status = input->connect_status;
  return true;
}

rei_robot_base__msg__CarData *
rei_robot_base__msg__CarData__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__msg__CarData * msg = (rei_robot_base__msg__CarData *)allocator.allocate(sizeof(rei_robot_base__msg__CarData), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rei_robot_base__msg__CarData));
  bool success = rei_robot_base__msg__CarData__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rei_robot_base__msg__CarData__destroy(rei_robot_base__msg__CarData * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rei_robot_base__msg__CarData__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rei_robot_base__msg__CarData__Sequence__init(rei_robot_base__msg__CarData__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__msg__CarData * data = NULL;

  if (size) {
    data = (rei_robot_base__msg__CarData *)allocator.zero_allocate(size, sizeof(rei_robot_base__msg__CarData), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rei_robot_base__msg__CarData__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rei_robot_base__msg__CarData__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
rei_robot_base__msg__CarData__Sequence__fini(rei_robot_base__msg__CarData__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      rei_robot_base__msg__CarData__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

rei_robot_base__msg__CarData__Sequence *
rei_robot_base__msg__CarData__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__msg__CarData__Sequence * array = (rei_robot_base__msg__CarData__Sequence *)allocator.allocate(sizeof(rei_robot_base__msg__CarData__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rei_robot_base__msg__CarData__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rei_robot_base__msg__CarData__Sequence__destroy(rei_robot_base__msg__CarData__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rei_robot_base__msg__CarData__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rei_robot_base__msg__CarData__Sequence__are_equal(const rei_robot_base__msg__CarData__Sequence * lhs, const rei_robot_base__msg__CarData__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rei_robot_base__msg__CarData__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rei_robot_base__msg__CarData__Sequence__copy(
  const rei_robot_base__msg__CarData__Sequence * input,
  rei_robot_base__msg__CarData__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rei_robot_base__msg__CarData);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rei_robot_base__msg__CarData * data =
      (rei_robot_base__msg__CarData *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rei_robot_base__msg__CarData__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rei_robot_base__msg__CarData__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rei_robot_base__msg__CarData__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
