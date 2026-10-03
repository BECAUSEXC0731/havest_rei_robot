// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rei_robot_base:srv/SetIO.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/srv/detail/set_io__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `io`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
rei_robot_base__srv__SetIO_Request__init(rei_robot_base__srv__SetIO_Request * msg)
{
  if (!msg) {
    return false;
  }
  // all_off
  // all_on
  // io
  if (!rosidl_runtime_c__int8__Sequence__init(&msg->io, 0)) {
    rei_robot_base__srv__SetIO_Request__fini(msg);
    return false;
  }
  // state
  return true;
}

void
rei_robot_base__srv__SetIO_Request__fini(rei_robot_base__srv__SetIO_Request * msg)
{
  if (!msg) {
    return;
  }
  // all_off
  // all_on
  // io
  rosidl_runtime_c__int8__Sequence__fini(&msg->io);
  // state
}

bool
rei_robot_base__srv__SetIO_Request__are_equal(const rei_robot_base__srv__SetIO_Request * lhs, const rei_robot_base__srv__SetIO_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // all_off
  if (lhs->all_off != rhs->all_off) {
    return false;
  }
  // all_on
  if (lhs->all_on != rhs->all_on) {
    return false;
  }
  // io
  if (!rosidl_runtime_c__int8__Sequence__are_equal(
      &(lhs->io), &(rhs->io)))
  {
    return false;
  }
  // state
  if (lhs->state != rhs->state) {
    return false;
  }
  return true;
}

bool
rei_robot_base__srv__SetIO_Request__copy(
  const rei_robot_base__srv__SetIO_Request * input,
  rei_robot_base__srv__SetIO_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // all_off
  output->all_off = input->all_off;
  // all_on
  output->all_on = input->all_on;
  // io
  if (!rosidl_runtime_c__int8__Sequence__copy(
      &(input->io), &(output->io)))
  {
    return false;
  }
  // state
  output->state = input->state;
  return true;
}

rei_robot_base__srv__SetIO_Request *
rei_robot_base__srv__SetIO_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__SetIO_Request * msg = (rei_robot_base__srv__SetIO_Request *)allocator.allocate(sizeof(rei_robot_base__srv__SetIO_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rei_robot_base__srv__SetIO_Request));
  bool success = rei_robot_base__srv__SetIO_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rei_robot_base__srv__SetIO_Request__destroy(rei_robot_base__srv__SetIO_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rei_robot_base__srv__SetIO_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rei_robot_base__srv__SetIO_Request__Sequence__init(rei_robot_base__srv__SetIO_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__SetIO_Request * data = NULL;

  if (size) {
    data = (rei_robot_base__srv__SetIO_Request *)allocator.zero_allocate(size, sizeof(rei_robot_base__srv__SetIO_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rei_robot_base__srv__SetIO_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rei_robot_base__srv__SetIO_Request__fini(&data[i - 1]);
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
rei_robot_base__srv__SetIO_Request__Sequence__fini(rei_robot_base__srv__SetIO_Request__Sequence * array)
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
      rei_robot_base__srv__SetIO_Request__fini(&array->data[i]);
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

rei_robot_base__srv__SetIO_Request__Sequence *
rei_robot_base__srv__SetIO_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__SetIO_Request__Sequence * array = (rei_robot_base__srv__SetIO_Request__Sequence *)allocator.allocate(sizeof(rei_robot_base__srv__SetIO_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rei_robot_base__srv__SetIO_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rei_robot_base__srv__SetIO_Request__Sequence__destroy(rei_robot_base__srv__SetIO_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rei_robot_base__srv__SetIO_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rei_robot_base__srv__SetIO_Request__Sequence__are_equal(const rei_robot_base__srv__SetIO_Request__Sequence * lhs, const rei_robot_base__srv__SetIO_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rei_robot_base__srv__SetIO_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rei_robot_base__srv__SetIO_Request__Sequence__copy(
  const rei_robot_base__srv__SetIO_Request__Sequence * input,
  rei_robot_base__srv__SetIO_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rei_robot_base__srv__SetIO_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rei_robot_base__srv__SetIO_Request * data =
      (rei_robot_base__srv__SetIO_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rei_robot_base__srv__SetIO_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rei_robot_base__srv__SetIO_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rei_robot_base__srv__SetIO_Request__copy(
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
rei_robot_base__srv__SetIO_Response__init(rei_robot_base__srv__SetIO_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    rei_robot_base__srv__SetIO_Response__fini(msg);
    return false;
  }
  return true;
}

void
rei_robot_base__srv__SetIO_Response__fini(rei_robot_base__srv__SetIO_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
rei_robot_base__srv__SetIO_Response__are_equal(const rei_robot_base__srv__SetIO_Response * lhs, const rei_robot_base__srv__SetIO_Response * rhs)
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
rei_robot_base__srv__SetIO_Response__copy(
  const rei_robot_base__srv__SetIO_Response * input,
  rei_robot_base__srv__SetIO_Response * output)
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

rei_robot_base__srv__SetIO_Response *
rei_robot_base__srv__SetIO_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__SetIO_Response * msg = (rei_robot_base__srv__SetIO_Response *)allocator.allocate(sizeof(rei_robot_base__srv__SetIO_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rei_robot_base__srv__SetIO_Response));
  bool success = rei_robot_base__srv__SetIO_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rei_robot_base__srv__SetIO_Response__destroy(rei_robot_base__srv__SetIO_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rei_robot_base__srv__SetIO_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rei_robot_base__srv__SetIO_Response__Sequence__init(rei_robot_base__srv__SetIO_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__SetIO_Response * data = NULL;

  if (size) {
    data = (rei_robot_base__srv__SetIO_Response *)allocator.zero_allocate(size, sizeof(rei_robot_base__srv__SetIO_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rei_robot_base__srv__SetIO_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rei_robot_base__srv__SetIO_Response__fini(&data[i - 1]);
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
rei_robot_base__srv__SetIO_Response__Sequence__fini(rei_robot_base__srv__SetIO_Response__Sequence * array)
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
      rei_robot_base__srv__SetIO_Response__fini(&array->data[i]);
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

rei_robot_base__srv__SetIO_Response__Sequence *
rei_robot_base__srv__SetIO_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__SetIO_Response__Sequence * array = (rei_robot_base__srv__SetIO_Response__Sequence *)allocator.allocate(sizeof(rei_robot_base__srv__SetIO_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rei_robot_base__srv__SetIO_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rei_robot_base__srv__SetIO_Response__Sequence__destroy(rei_robot_base__srv__SetIO_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rei_robot_base__srv__SetIO_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rei_robot_base__srv__SetIO_Response__Sequence__are_equal(const rei_robot_base__srv__SetIO_Response__Sequence * lhs, const rei_robot_base__srv__SetIO_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rei_robot_base__srv__SetIO_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rei_robot_base__srv__SetIO_Response__Sequence__copy(
  const rei_robot_base__srv__SetIO_Response__Sequence * input,
  rei_robot_base__srv__SetIO_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rei_robot_base__srv__SetIO_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rei_robot_base__srv__SetIO_Response * data =
      (rei_robot_base__srv__SetIO_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rei_robot_base__srv__SetIO_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rei_robot_base__srv__SetIO_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rei_robot_base__srv__SetIO_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
