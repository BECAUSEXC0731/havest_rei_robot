// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rei_robot_base:msg/MotorCmd.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/msg/detail/motor_cmd__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `motor_expect_speed`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
rei_robot_base__msg__MotorCmd__init(rei_robot_base__msg__MotorCmd * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    rei_robot_base__msg__MotorCmd__fini(msg);
    return false;
  }
  // motor_expect_speed
  if (!rosidl_runtime_c__double__Sequence__init(&msg->motor_expect_speed, 0)) {
    rei_robot_base__msg__MotorCmd__fini(msg);
    return false;
  }
  return true;
}

void
rei_robot_base__msg__MotorCmd__fini(rei_robot_base__msg__MotorCmd * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // motor_expect_speed
  rosidl_runtime_c__double__Sequence__fini(&msg->motor_expect_speed);
}

bool
rei_robot_base__msg__MotorCmd__are_equal(const rei_robot_base__msg__MotorCmd * lhs, const rei_robot_base__msg__MotorCmd * rhs)
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
  // motor_expect_speed
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->motor_expect_speed), &(rhs->motor_expect_speed)))
  {
    return false;
  }
  return true;
}

bool
rei_robot_base__msg__MotorCmd__copy(
  const rei_robot_base__msg__MotorCmd * input,
  rei_robot_base__msg__MotorCmd * output)
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
  // motor_expect_speed
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->motor_expect_speed), &(output->motor_expect_speed)))
  {
    return false;
  }
  return true;
}

rei_robot_base__msg__MotorCmd *
rei_robot_base__msg__MotorCmd__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__msg__MotorCmd * msg = (rei_robot_base__msg__MotorCmd *)allocator.allocate(sizeof(rei_robot_base__msg__MotorCmd), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rei_robot_base__msg__MotorCmd));
  bool success = rei_robot_base__msg__MotorCmd__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rei_robot_base__msg__MotorCmd__destroy(rei_robot_base__msg__MotorCmd * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rei_robot_base__msg__MotorCmd__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rei_robot_base__msg__MotorCmd__Sequence__init(rei_robot_base__msg__MotorCmd__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__msg__MotorCmd * data = NULL;

  if (size) {
    data = (rei_robot_base__msg__MotorCmd *)allocator.zero_allocate(size, sizeof(rei_robot_base__msg__MotorCmd), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rei_robot_base__msg__MotorCmd__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rei_robot_base__msg__MotorCmd__fini(&data[i - 1]);
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
rei_robot_base__msg__MotorCmd__Sequence__fini(rei_robot_base__msg__MotorCmd__Sequence * array)
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
      rei_robot_base__msg__MotorCmd__fini(&array->data[i]);
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

rei_robot_base__msg__MotorCmd__Sequence *
rei_robot_base__msg__MotorCmd__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__msg__MotorCmd__Sequence * array = (rei_robot_base__msg__MotorCmd__Sequence *)allocator.allocate(sizeof(rei_robot_base__msg__MotorCmd__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rei_robot_base__msg__MotorCmd__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rei_robot_base__msg__MotorCmd__Sequence__destroy(rei_robot_base__msg__MotorCmd__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rei_robot_base__msg__MotorCmd__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rei_robot_base__msg__MotorCmd__Sequence__are_equal(const rei_robot_base__msg__MotorCmd__Sequence * lhs, const rei_robot_base__msg__MotorCmd__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rei_robot_base__msg__MotorCmd__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rei_robot_base__msg__MotorCmd__Sequence__copy(
  const rei_robot_base__msg__MotorCmd__Sequence * input,
  rei_robot_base__msg__MotorCmd__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rei_robot_base__msg__MotorCmd);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rei_robot_base__msg__MotorCmd * data =
      (rei_robot_base__msg__MotorCmd *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rei_robot_base__msg__MotorCmd__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rei_robot_base__msg__MotorCmd__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rei_robot_base__msg__MotorCmd__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
