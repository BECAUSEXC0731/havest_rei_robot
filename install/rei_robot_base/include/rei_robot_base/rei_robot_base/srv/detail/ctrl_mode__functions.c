// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rei_robot_base:srv/CtrlMode.idl
// generated code does not contain a copyright notice
#include "rei_robot_base/srv/detail/ctrl_mode__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
rei_robot_base__srv__CtrlMode_Request__init(rei_robot_base__srv__CtrlMode_Request * msg)
{
  if (!msg) {
    return false;
  }
  // ctrl_mode
  // use_acc
  return true;
}

void
rei_robot_base__srv__CtrlMode_Request__fini(rei_robot_base__srv__CtrlMode_Request * msg)
{
  if (!msg) {
    return;
  }
  // ctrl_mode
  // use_acc
}

bool
rei_robot_base__srv__CtrlMode_Request__are_equal(const rei_robot_base__srv__CtrlMode_Request * lhs, const rei_robot_base__srv__CtrlMode_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // ctrl_mode
  if (lhs->ctrl_mode != rhs->ctrl_mode) {
    return false;
  }
  // use_acc
  if (lhs->use_acc != rhs->use_acc) {
    return false;
  }
  return true;
}

bool
rei_robot_base__srv__CtrlMode_Request__copy(
  const rei_robot_base__srv__CtrlMode_Request * input,
  rei_robot_base__srv__CtrlMode_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // ctrl_mode
  output->ctrl_mode = input->ctrl_mode;
  // use_acc
  output->use_acc = input->use_acc;
  return true;
}

rei_robot_base__srv__CtrlMode_Request *
rei_robot_base__srv__CtrlMode_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__CtrlMode_Request * msg = (rei_robot_base__srv__CtrlMode_Request *)allocator.allocate(sizeof(rei_robot_base__srv__CtrlMode_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rei_robot_base__srv__CtrlMode_Request));
  bool success = rei_robot_base__srv__CtrlMode_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rei_robot_base__srv__CtrlMode_Request__destroy(rei_robot_base__srv__CtrlMode_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rei_robot_base__srv__CtrlMode_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rei_robot_base__srv__CtrlMode_Request__Sequence__init(rei_robot_base__srv__CtrlMode_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__CtrlMode_Request * data = NULL;

  if (size) {
    data = (rei_robot_base__srv__CtrlMode_Request *)allocator.zero_allocate(size, sizeof(rei_robot_base__srv__CtrlMode_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rei_robot_base__srv__CtrlMode_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rei_robot_base__srv__CtrlMode_Request__fini(&data[i - 1]);
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
rei_robot_base__srv__CtrlMode_Request__Sequence__fini(rei_robot_base__srv__CtrlMode_Request__Sequence * array)
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
      rei_robot_base__srv__CtrlMode_Request__fini(&array->data[i]);
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

rei_robot_base__srv__CtrlMode_Request__Sequence *
rei_robot_base__srv__CtrlMode_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__CtrlMode_Request__Sequence * array = (rei_robot_base__srv__CtrlMode_Request__Sequence *)allocator.allocate(sizeof(rei_robot_base__srv__CtrlMode_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rei_robot_base__srv__CtrlMode_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rei_robot_base__srv__CtrlMode_Request__Sequence__destroy(rei_robot_base__srv__CtrlMode_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rei_robot_base__srv__CtrlMode_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rei_robot_base__srv__CtrlMode_Request__Sequence__are_equal(const rei_robot_base__srv__CtrlMode_Request__Sequence * lhs, const rei_robot_base__srv__CtrlMode_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rei_robot_base__srv__CtrlMode_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rei_robot_base__srv__CtrlMode_Request__Sequence__copy(
  const rei_robot_base__srv__CtrlMode_Request__Sequence * input,
  rei_robot_base__srv__CtrlMode_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rei_robot_base__srv__CtrlMode_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rei_robot_base__srv__CtrlMode_Request * data =
      (rei_robot_base__srv__CtrlMode_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rei_robot_base__srv__CtrlMode_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rei_robot_base__srv__CtrlMode_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rei_robot_base__srv__CtrlMode_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
rei_robot_base__srv__CtrlMode_Response__init(rei_robot_base__srv__CtrlMode_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  return true;
}

void
rei_robot_base__srv__CtrlMode_Response__fini(rei_robot_base__srv__CtrlMode_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
}

bool
rei_robot_base__srv__CtrlMode_Response__are_equal(const rei_robot_base__srv__CtrlMode_Response * lhs, const rei_robot_base__srv__CtrlMode_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  return true;
}

bool
rei_robot_base__srv__CtrlMode_Response__copy(
  const rei_robot_base__srv__CtrlMode_Response * input,
  rei_robot_base__srv__CtrlMode_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  return true;
}

rei_robot_base__srv__CtrlMode_Response *
rei_robot_base__srv__CtrlMode_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__CtrlMode_Response * msg = (rei_robot_base__srv__CtrlMode_Response *)allocator.allocate(sizeof(rei_robot_base__srv__CtrlMode_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rei_robot_base__srv__CtrlMode_Response));
  bool success = rei_robot_base__srv__CtrlMode_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rei_robot_base__srv__CtrlMode_Response__destroy(rei_robot_base__srv__CtrlMode_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rei_robot_base__srv__CtrlMode_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rei_robot_base__srv__CtrlMode_Response__Sequence__init(rei_robot_base__srv__CtrlMode_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__CtrlMode_Response * data = NULL;

  if (size) {
    data = (rei_robot_base__srv__CtrlMode_Response *)allocator.zero_allocate(size, sizeof(rei_robot_base__srv__CtrlMode_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rei_robot_base__srv__CtrlMode_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rei_robot_base__srv__CtrlMode_Response__fini(&data[i - 1]);
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
rei_robot_base__srv__CtrlMode_Response__Sequence__fini(rei_robot_base__srv__CtrlMode_Response__Sequence * array)
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
      rei_robot_base__srv__CtrlMode_Response__fini(&array->data[i]);
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

rei_robot_base__srv__CtrlMode_Response__Sequence *
rei_robot_base__srv__CtrlMode_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rei_robot_base__srv__CtrlMode_Response__Sequence * array = (rei_robot_base__srv__CtrlMode_Response__Sequence *)allocator.allocate(sizeof(rei_robot_base__srv__CtrlMode_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rei_robot_base__srv__CtrlMode_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rei_robot_base__srv__CtrlMode_Response__Sequence__destroy(rei_robot_base__srv__CtrlMode_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rei_robot_base__srv__CtrlMode_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rei_robot_base__srv__CtrlMode_Response__Sequence__are_equal(const rei_robot_base__srv__CtrlMode_Response__Sequence * lhs, const rei_robot_base__srv__CtrlMode_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rei_robot_base__srv__CtrlMode_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rei_robot_base__srv__CtrlMode_Response__Sequence__copy(
  const rei_robot_base__srv__CtrlMode_Response__Sequence * input,
  rei_robot_base__srv__CtrlMode_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rei_robot_base__srv__CtrlMode_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rei_robot_base__srv__CtrlMode_Response * data =
      (rei_robot_base__srv__CtrlMode_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rei_robot_base__srv__CtrlMode_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rei_robot_base__srv__CtrlMode_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rei_robot_base__srv__CtrlMode_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
