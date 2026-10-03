// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from arm_controller:msg/Control.idl
// generated code does not contain a copyright notice
#include "arm_controller/msg/detail/control__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `position`
#include "geometry_msgs/msg/detail/point__functions.h"

bool
arm_controller__msg__Control__init(arm_controller__msg__Control * msg)
{
  if (!msg) {
    return false;
  }
  // position
  if (!geometry_msgs__msg__Point__init(&msg->position)) {
    arm_controller__msg__Control__fini(msg);
    return false;
  }
  // roll
  // pitch
  // yaw
  return true;
}

void
arm_controller__msg__Control__fini(arm_controller__msg__Control * msg)
{
  if (!msg) {
    return;
  }
  // position
  geometry_msgs__msg__Point__fini(&msg->position);
  // roll
  // pitch
  // yaw
}

bool
arm_controller__msg__Control__are_equal(const arm_controller__msg__Control * lhs, const arm_controller__msg__Control * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // position
  if (!geometry_msgs__msg__Point__are_equal(
      &(lhs->position), &(rhs->position)))
  {
    return false;
  }
  // roll
  if (lhs->roll != rhs->roll) {
    return false;
  }
  // pitch
  if (lhs->pitch != rhs->pitch) {
    return false;
  }
  // yaw
  if (lhs->yaw != rhs->yaw) {
    return false;
  }
  return true;
}

bool
arm_controller__msg__Control__copy(
  const arm_controller__msg__Control * input,
  arm_controller__msg__Control * output)
{
  if (!input || !output) {
    return false;
  }
  // position
  if (!geometry_msgs__msg__Point__copy(
      &(input->position), &(output->position)))
  {
    return false;
  }
  // roll
  output->roll = input->roll;
  // pitch
  output->pitch = input->pitch;
  // yaw
  output->yaw = input->yaw;
  return true;
}

arm_controller__msg__Control *
arm_controller__msg__Control__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__msg__Control * msg = (arm_controller__msg__Control *)allocator.allocate(sizeof(arm_controller__msg__Control), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(arm_controller__msg__Control));
  bool success = arm_controller__msg__Control__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
arm_controller__msg__Control__destroy(arm_controller__msg__Control * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    arm_controller__msg__Control__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
arm_controller__msg__Control__Sequence__init(arm_controller__msg__Control__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__msg__Control * data = NULL;

  if (size) {
    data = (arm_controller__msg__Control *)allocator.zero_allocate(size, sizeof(arm_controller__msg__Control), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = arm_controller__msg__Control__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        arm_controller__msg__Control__fini(&data[i - 1]);
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
arm_controller__msg__Control__Sequence__fini(arm_controller__msg__Control__Sequence * array)
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
      arm_controller__msg__Control__fini(&array->data[i]);
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

arm_controller__msg__Control__Sequence *
arm_controller__msg__Control__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__msg__Control__Sequence * array = (arm_controller__msg__Control__Sequence *)allocator.allocate(sizeof(arm_controller__msg__Control__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = arm_controller__msg__Control__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
arm_controller__msg__Control__Sequence__destroy(arm_controller__msg__Control__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    arm_controller__msg__Control__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
arm_controller__msg__Control__Sequence__are_equal(const arm_controller__msg__Control__Sequence * lhs, const arm_controller__msg__Control__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!arm_controller__msg__Control__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
arm_controller__msg__Control__Sequence__copy(
  const arm_controller__msg__Control__Sequence * input,
  arm_controller__msg__Control__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(arm_controller__msg__Control);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    arm_controller__msg__Control * data =
      (arm_controller__msg__Control *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!arm_controller__msg__Control__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          arm_controller__msg__Control__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!arm_controller__msg__Control__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
