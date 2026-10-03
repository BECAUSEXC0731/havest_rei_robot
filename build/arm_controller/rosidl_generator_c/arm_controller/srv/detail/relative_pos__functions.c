// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from arm_controller:srv/RelativePos.idl
// generated code does not contain a copyright notice
#include "arm_controller/srv/detail/relative_pos__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
arm_controller__srv__RelativePos_Request__init(arm_controller__srv__RelativePos_Request * msg)
{
  if (!msg) {
    return false;
  }
  // dx
  // dy
  // dz
  return true;
}

void
arm_controller__srv__RelativePos_Request__fini(arm_controller__srv__RelativePos_Request * msg)
{
  if (!msg) {
    return;
  }
  // dx
  // dy
  // dz
}

bool
arm_controller__srv__RelativePos_Request__are_equal(const arm_controller__srv__RelativePos_Request * lhs, const arm_controller__srv__RelativePos_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // dx
  if (lhs->dx != rhs->dx) {
    return false;
  }
  // dy
  if (lhs->dy != rhs->dy) {
    return false;
  }
  // dz
  if (lhs->dz != rhs->dz) {
    return false;
  }
  return true;
}

bool
arm_controller__srv__RelativePos_Request__copy(
  const arm_controller__srv__RelativePos_Request * input,
  arm_controller__srv__RelativePos_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // dx
  output->dx = input->dx;
  // dy
  output->dy = input->dy;
  // dz
  output->dz = input->dz;
  return true;
}

arm_controller__srv__RelativePos_Request *
arm_controller__srv__RelativePos_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__RelativePos_Request * msg = (arm_controller__srv__RelativePos_Request *)allocator.allocate(sizeof(arm_controller__srv__RelativePos_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(arm_controller__srv__RelativePos_Request));
  bool success = arm_controller__srv__RelativePos_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
arm_controller__srv__RelativePos_Request__destroy(arm_controller__srv__RelativePos_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    arm_controller__srv__RelativePos_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
arm_controller__srv__RelativePos_Request__Sequence__init(arm_controller__srv__RelativePos_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__RelativePos_Request * data = NULL;

  if (size) {
    data = (arm_controller__srv__RelativePos_Request *)allocator.zero_allocate(size, sizeof(arm_controller__srv__RelativePos_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = arm_controller__srv__RelativePos_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        arm_controller__srv__RelativePos_Request__fini(&data[i - 1]);
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
arm_controller__srv__RelativePos_Request__Sequence__fini(arm_controller__srv__RelativePos_Request__Sequence * array)
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
      arm_controller__srv__RelativePos_Request__fini(&array->data[i]);
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

arm_controller__srv__RelativePos_Request__Sequence *
arm_controller__srv__RelativePos_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__RelativePos_Request__Sequence * array = (arm_controller__srv__RelativePos_Request__Sequence *)allocator.allocate(sizeof(arm_controller__srv__RelativePos_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = arm_controller__srv__RelativePos_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
arm_controller__srv__RelativePos_Request__Sequence__destroy(arm_controller__srv__RelativePos_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    arm_controller__srv__RelativePos_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
arm_controller__srv__RelativePos_Request__Sequence__are_equal(const arm_controller__srv__RelativePos_Request__Sequence * lhs, const arm_controller__srv__RelativePos_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!arm_controller__srv__RelativePos_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
arm_controller__srv__RelativePos_Request__Sequence__copy(
  const arm_controller__srv__RelativePos_Request__Sequence * input,
  arm_controller__srv__RelativePos_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(arm_controller__srv__RelativePos_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    arm_controller__srv__RelativePos_Request * data =
      (arm_controller__srv__RelativePos_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!arm_controller__srv__RelativePos_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          arm_controller__srv__RelativePos_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!arm_controller__srv__RelativePos_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
arm_controller__srv__RelativePos_Response__init(arm_controller__srv__RelativePos_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    arm_controller__srv__RelativePos_Response__fini(msg);
    return false;
  }
  return true;
}

void
arm_controller__srv__RelativePos_Response__fini(arm_controller__srv__RelativePos_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
arm_controller__srv__RelativePos_Response__are_equal(const arm_controller__srv__RelativePos_Response * lhs, const arm_controller__srv__RelativePos_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
arm_controller__srv__RelativePos_Response__copy(
  const arm_controller__srv__RelativePos_Response * input,
  arm_controller__srv__RelativePos_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

arm_controller__srv__RelativePos_Response *
arm_controller__srv__RelativePos_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__RelativePos_Response * msg = (arm_controller__srv__RelativePos_Response *)allocator.allocate(sizeof(arm_controller__srv__RelativePos_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(arm_controller__srv__RelativePos_Response));
  bool success = arm_controller__srv__RelativePos_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
arm_controller__srv__RelativePos_Response__destroy(arm_controller__srv__RelativePos_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    arm_controller__srv__RelativePos_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
arm_controller__srv__RelativePos_Response__Sequence__init(arm_controller__srv__RelativePos_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__RelativePos_Response * data = NULL;

  if (size) {
    data = (arm_controller__srv__RelativePos_Response *)allocator.zero_allocate(size, sizeof(arm_controller__srv__RelativePos_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = arm_controller__srv__RelativePos_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        arm_controller__srv__RelativePos_Response__fini(&data[i - 1]);
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
arm_controller__srv__RelativePos_Response__Sequence__fini(arm_controller__srv__RelativePos_Response__Sequence * array)
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
      arm_controller__srv__RelativePos_Response__fini(&array->data[i]);
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

arm_controller__srv__RelativePos_Response__Sequence *
arm_controller__srv__RelativePos_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  arm_controller__srv__RelativePos_Response__Sequence * array = (arm_controller__srv__RelativePos_Response__Sequence *)allocator.allocate(sizeof(arm_controller__srv__RelativePos_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = arm_controller__srv__RelativePos_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
arm_controller__srv__RelativePos_Response__Sequence__destroy(arm_controller__srv__RelativePos_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    arm_controller__srv__RelativePos_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
arm_controller__srv__RelativePos_Response__Sequence__are_equal(const arm_controller__srv__RelativePos_Response__Sequence * lhs, const arm_controller__srv__RelativePos_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!arm_controller__srv__RelativePos_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
arm_controller__srv__RelativePos_Response__Sequence__copy(
  const arm_controller__srv__RelativePos_Response__Sequence * input,
  arm_controller__srv__RelativePos_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(arm_controller__srv__RelativePos_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    arm_controller__srv__RelativePos_Response * data =
      (arm_controller__srv__RelativePos_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!arm_controller__srv__RelativePos_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          arm_controller__srv__RelativePos_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!arm_controller__srv__RelativePos_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
