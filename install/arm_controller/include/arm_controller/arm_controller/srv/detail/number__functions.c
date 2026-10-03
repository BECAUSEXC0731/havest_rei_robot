// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from arm_controller:srv/Number.idl
// generated code does not contain a copyright notice
#include "arm_controller/srv/detail/number__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
arm_controller__srv__Number_Request__init(arm_controller__srv__Number_Request * msg)
{
  if (!msg) {
    return false;
  }
  // data
  return true;
}

void
arm_controller__srv__Number_Request__fini(arm_controller__srv__Number_Request * msg)
{
  if (!msg) {
    return;
  }
  // data
}

bool
arm_controller__srv__Number_Request__are_equal(const arm_controller__srv__Number_Request * lhs, const arm_controller__srv__Number_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // data
  if (lhs->data != rhs->data) {
    return false;
  }
  return true;
}

bool
arm_controller__srv__Number_Request__copy(
  const arm_controller__srv__Number_Request * input,
  arm_controller__srv__Number_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // data
  output->data = input->data;
  return true;
}

arm_controller__srv__Number_Request *
arm_controller__srv__Number_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__Number_Request * msg = (arm_controller__srv__Number_Request *)allocator.allocate(sizeof(arm_controller__srv__Number_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(arm_controller__srv__Number_Request));
  bool success = arm_controller__srv__Number_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
arm_controller__srv__Number_Request__destroy(arm_controller__srv__Number_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    arm_controller__srv__Number_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
arm_controller__srv__Number_Request__Sequence__init(arm_controller__srv__Number_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__Number_Request * data = NULL;

  if (size) {
    data = (arm_controller__srv__Number_Request *)allocator.zero_allocate(size, sizeof(arm_controller__srv__Number_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = arm_controller__srv__Number_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        arm_controller__srv__Number_Request__fini(&data[i - 1]);
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
arm_controller__srv__Number_Request__Sequence__fini(arm_controller__srv__Number_Request__Sequence * array)
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
      arm_controller__srv__Number_Request__fini(&array->data[i]);
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

arm_controller__srv__Number_Request__Sequence *
arm_controller__srv__Number_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__Number_Request__Sequence * array = (arm_controller__srv__Number_Request__Sequence *)allocator.allocate(sizeof(arm_controller__srv__Number_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = arm_controller__srv__Number_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
arm_controller__srv__Number_Request__Sequence__destroy(arm_controller__srv__Number_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    arm_controller__srv__Number_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
arm_controller__srv__Number_Request__Sequence__are_equal(const arm_controller__srv__Number_Request__Sequence * lhs, const arm_controller__srv__Number_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!arm_controller__srv__Number_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
arm_controller__srv__Number_Request__Sequence__copy(
  const arm_controller__srv__Number_Request__Sequence * input,
  arm_controller__srv__Number_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(arm_controller__srv__Number_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    arm_controller__srv__Number_Request * data =
      (arm_controller__srv__Number_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!arm_controller__srv__Number_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          arm_controller__srv__Number_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!arm_controller__srv__Number_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `number`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `pose`
#include "arm_controller/msg/detail/control__functions.h"

bool
arm_controller__srv__Number_Response__init(arm_controller__srv__Number_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // number
  if (!rosidl_runtime_c__int8__Sequence__init(&msg->number, 0)) {
    arm_controller__srv__Number_Response__fini(msg);
    return false;
  }
  // pose
  if (!arm_controller__msg__Control__Sequence__init(&msg->pose, 0)) {
    arm_controller__srv__Number_Response__fini(msg);
    return false;
  }
  return true;
}

void
arm_controller__srv__Number_Response__fini(arm_controller__srv__Number_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // number
  rosidl_runtime_c__int8__Sequence__fini(&msg->number);
  // pose
  arm_controller__msg__Control__Sequence__fini(&msg->pose);
}

bool
arm_controller__srv__Number_Response__are_equal(const arm_controller__srv__Number_Response * lhs, const arm_controller__srv__Number_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // number
  if (!rosidl_runtime_c__int8__Sequence__are_equal(
      &(lhs->number), &(rhs->number)))
  {
    return false;
  }
  // pose
  if (!arm_controller__msg__Control__Sequence__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  return true;
}

bool
arm_controller__srv__Number_Response__copy(
  const arm_controller__srv__Number_Response * input,
  arm_controller__srv__Number_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // number
  if (!rosidl_runtime_c__int8__Sequence__copy(
      &(input->number), &(output->number)))
  {
    return false;
  }
  // pose
  if (!arm_controller__msg__Control__Sequence__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  return true;
}

arm_controller__srv__Number_Response *
arm_controller__srv__Number_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__Number_Response * msg = (arm_controller__srv__Number_Response *)allocator.allocate(sizeof(arm_controller__srv__Number_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(arm_controller__srv__Number_Response));
  bool success = arm_controller__srv__Number_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
arm_controller__srv__Number_Response__destroy(arm_controller__srv__Number_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    arm_controller__srv__Number_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
arm_controller__srv__Number_Response__Sequence__init(arm_controller__srv__Number_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__Number_Response * data = NULL;

  if (size) {
    data = (arm_controller__srv__Number_Response *)allocator.zero_allocate(size, sizeof(arm_controller__srv__Number_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = arm_controller__srv__Number_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        arm_controller__srv__Number_Response__fini(&data[i - 1]);
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
arm_controller__srv__Number_Response__Sequence__fini(arm_controller__srv__Number_Response__Sequence * array)
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
      arm_controller__srv__Number_Response__fini(&array->data[i]);
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

arm_controller__srv__Number_Response__Sequence *
arm_controller__srv__Number_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__Number_Response__Sequence * array = (arm_controller__srv__Number_Response__Sequence *)allocator.allocate(sizeof(arm_controller__srv__Number_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = arm_controller__srv__Number_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
arm_controller__srv__Number_Response__Sequence__destroy(arm_controller__srv__Number_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    arm_controller__srv__Number_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
arm_controller__srv__Number_Response__Sequence__are_equal(const arm_controller__srv__Number_Response__Sequence * lhs, const arm_controller__srv__Number_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!arm_controller__srv__Number_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
arm_controller__srv__Number_Response__Sequence__copy(
  const arm_controller__srv__Number_Response__Sequence * input,
  arm_controller__srv__Number_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(arm_controller__srv__Number_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    arm_controller__srv__Number_Response * data =
      (arm_controller__srv__Number_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!arm_controller__srv__Number_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          arm_controller__srv__Number_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!arm_controller__srv__Number_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
