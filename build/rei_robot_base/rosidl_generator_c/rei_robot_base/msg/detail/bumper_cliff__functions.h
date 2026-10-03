// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from rei_robot_base:msg/BumperCliff.idl
// generated code does not contain a copyright notice

#ifndef REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__FUNCTIONS_H_
#define REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "rei_robot_base/msg/rosidl_generator_c__visibility_control.h"

#include "rei_robot_base/msg/detail/bumper_cliff__struct.h"

/// Initialize msg/BumperCliff message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * rei_robot_base__msg__BumperCliff
 * )) before or use
 * rei_robot_base__msg__BumperCliff__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
bool
rei_robot_base__msg__BumperCliff__init(rei_robot_base__msg__BumperCliff * msg);

/// Finalize msg/BumperCliff message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
void
rei_robot_base__msg__BumperCliff__fini(rei_robot_base__msg__BumperCliff * msg);

/// Create msg/BumperCliff message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * rei_robot_base__msg__BumperCliff__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
rei_robot_base__msg__BumperCliff *
rei_robot_base__msg__BumperCliff__create();

/// Destroy msg/BumperCliff message.
/**
 * It calls
 * rei_robot_base__msg__BumperCliff__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
void
rei_robot_base__msg__BumperCliff__destroy(rei_robot_base__msg__BumperCliff * msg);

/// Check for msg/BumperCliff message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
bool
rei_robot_base__msg__BumperCliff__are_equal(const rei_robot_base__msg__BumperCliff * lhs, const rei_robot_base__msg__BumperCliff * rhs);

/// Copy a msg/BumperCliff message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
bool
rei_robot_base__msg__BumperCliff__copy(
  const rei_robot_base__msg__BumperCliff * input,
  rei_robot_base__msg__BumperCliff * output);

/// Initialize array of msg/BumperCliff messages.
/**
 * It allocates the memory for the number of elements and calls
 * rei_robot_base__msg__BumperCliff__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
bool
rei_robot_base__msg__BumperCliff__Sequence__init(rei_robot_base__msg__BumperCliff__Sequence * array, size_t size);

/// Finalize array of msg/BumperCliff messages.
/**
 * It calls
 * rei_robot_base__msg__BumperCliff__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
void
rei_robot_base__msg__BumperCliff__Sequence__fini(rei_robot_base__msg__BumperCliff__Sequence * array);

/// Create array of msg/BumperCliff messages.
/**
 * It allocates the memory for the array and calls
 * rei_robot_base__msg__BumperCliff__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
rei_robot_base__msg__BumperCliff__Sequence *
rei_robot_base__msg__BumperCliff__Sequence__create(size_t size);

/// Destroy array of msg/BumperCliff messages.
/**
 * It calls
 * rei_robot_base__msg__BumperCliff__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
void
rei_robot_base__msg__BumperCliff__Sequence__destroy(rei_robot_base__msg__BumperCliff__Sequence * array);

/// Check for msg/BumperCliff message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
bool
rei_robot_base__msg__BumperCliff__Sequence__are_equal(const rei_robot_base__msg__BumperCliff__Sequence * lhs, const rei_robot_base__msg__BumperCliff__Sequence * rhs);

/// Copy an array of msg/BumperCliff messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_rei_robot_base
bool
rei_robot_base__msg__BumperCliff__Sequence__copy(
  const rei_robot_base__msg__BumperCliff__Sequence * input,
  rei_robot_base__msg__BumperCliff__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // REI_ROBOT_BASE__MSG__DETAIL__BUMPER_CLIFF__FUNCTIONS_H_
