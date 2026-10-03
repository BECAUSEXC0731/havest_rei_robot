// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from rei_robot_base:msg/BumperCliff.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "rei_robot_base/msg/detail/bumper_cliff__struct.h"
#include "rei_robot_base/msg/detail/bumper_cliff__functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool rei_robot_base__msg__bumper_cliff__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[45];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("rei_robot_base.msg._bumper_cliff.BumperCliff", full_classname_dest, 44) == 0);
  }
  rei_robot_base__msg__BumperCliff * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // bumper
    PyObject * field = PyObject_GetAttrString(_pymsg, "bumper");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->bumper = (Py_True == field);
    Py_DECREF(field);
  }
  {  // cliff
    PyObject * field = PyObject_GetAttrString(_pymsg, "cliff");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->cliff = (Py_True == field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * rei_robot_base__msg__bumper_cliff__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of BumperCliff */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("rei_robot_base.msg._bumper_cliff");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "BumperCliff");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  rei_robot_base__msg__BumperCliff * ros_message = (rei_robot_base__msg__BumperCliff *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // bumper
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->bumper ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "bumper", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // cliff
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->cliff ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "cliff", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
