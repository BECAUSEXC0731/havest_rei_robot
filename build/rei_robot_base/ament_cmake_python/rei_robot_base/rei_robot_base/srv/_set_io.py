# generated from rosidl_generator_py/resource/_idl.py.em
# with input from rei_robot_base:srv/SetIO.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'io'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SetIO_Request(type):
    """Metaclass of message 'SetIO_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('rei_robot_base')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'rei_robot_base.srv.SetIO_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_io__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_io__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_io__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_io__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_io__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetIO_Request(metaclass=Metaclass_SetIO_Request):
    """Message class 'SetIO_Request'."""

    __slots__ = [
        '_all_off',
        '_all_on',
        '_io',
        '_state',
    ]

    _fields_and_field_types = {
        'all_off': 'boolean',
        'all_on': 'boolean',
        'io': 'sequence<int8>',
        'state': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int8')),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.all_off = kwargs.get('all_off', bool())
        self.all_on = kwargs.get('all_on', bool())
        self.io = array.array('b', kwargs.get('io', []))
        self.state = kwargs.get('state', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.all_off != other.all_off:
            return False
        if self.all_on != other.all_on:
            return False
        if self.io != other.io:
            return False
        if self.state != other.state:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def all_off(self):
        """Message field 'all_off'."""
        return self._all_off

    @all_off.setter
    def all_off(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'all_off' field must be of type 'bool'"
        self._all_off = value

    @builtins.property
    def all_on(self):
        """Message field 'all_on'."""
        return self._all_on

    @all_on.setter
    def all_on(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'all_on' field must be of type 'bool'"
        self._all_on = value

    @builtins.property
    def io(self):
        """Message field 'io'."""
        return self._io

    @io.setter
    def io(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'b', \
                "The 'io' array.array() must have the type code of 'b'"
            self._io = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -128 and val < 128 for val in value)), \
                "The 'io' field must be a set or sequence and each value of type 'int' and each integer in [-128, 127]"
        self._io = array.array('b', value)

    @builtins.property
    def state(self):
        """Message field 'state'."""
        return self._state

    @state.setter
    def state(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'state' field must be of type 'bool'"
        self._state = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_SetIO_Response(type):
    """Metaclass of message 'SetIO_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('rei_robot_base')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'rei_robot_base.srv.SetIO_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_io__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_io__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_io__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_io__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_io__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetIO_Response(metaclass=Metaclass_SetIO_Response):
    """Message class 'SetIO_Response'."""

    __slots__ = [
        '_success',
        '_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.message = kwargs.get('message', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.success != other.success:
            return False
        if self.message != other.message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def message(self):
        """Message field 'message'."""
        return self._message

    @message.setter
    def message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'message' field must be of type 'str'"
        self._message = value


class Metaclass_SetIO(type):
    """Metaclass of service 'SetIO'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('rei_robot_base')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'rei_robot_base.srv.SetIO')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__set_io

            from rei_robot_base.srv import _set_io
            if _set_io.Metaclass_SetIO_Request._TYPE_SUPPORT is None:
                _set_io.Metaclass_SetIO_Request.__import_type_support__()
            if _set_io.Metaclass_SetIO_Response._TYPE_SUPPORT is None:
                _set_io.Metaclass_SetIO_Response.__import_type_support__()


class SetIO(metaclass=Metaclass_SetIO):
    from rei_robot_base.srv._set_io import SetIO_Request as Request
    from rei_robot_base.srv._set_io import SetIO_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
