# generated from rosidl_generator_py/resource/_idl.py.em
# with input from rei_robot_base:srv/CtrlMode.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_CtrlMode_Request(type):
    """Metaclass of message 'CtrlMode_Request'."""

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
                'rei_robot_base.srv.CtrlMode_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__ctrl_mode__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__ctrl_mode__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__ctrl_mode__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__ctrl_mode__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__ctrl_mode__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class CtrlMode_Request(metaclass=Metaclass_CtrlMode_Request):
    """Message class 'CtrlMode_Request'."""

    __slots__ = [
        '_ctrl_mode',
        '_use_acc',
    ]

    _fields_and_field_types = {
        'ctrl_mode': 'int8',
        'use_acc': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.ctrl_mode = kwargs.get('ctrl_mode', int())
        self.use_acc = kwargs.get('use_acc', bool())

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
        if self.ctrl_mode != other.ctrl_mode:
            return False
        if self.use_acc != other.use_acc:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def ctrl_mode(self):
        """Message field 'ctrl_mode'."""
        return self._ctrl_mode

    @ctrl_mode.setter
    def ctrl_mode(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'ctrl_mode' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'ctrl_mode' field must be an integer in [-128, 127]"
        self._ctrl_mode = value

    @builtins.property
    def use_acc(self):
        """Message field 'use_acc'."""
        return self._use_acc

    @use_acc.setter
    def use_acc(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'use_acc' field must be of type 'bool'"
        self._use_acc = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_CtrlMode_Response(type):
    """Metaclass of message 'CtrlMode_Response'."""

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
                'rei_robot_base.srv.CtrlMode_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__ctrl_mode__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__ctrl_mode__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__ctrl_mode__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__ctrl_mode__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__ctrl_mode__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class CtrlMode_Response(metaclass=Metaclass_CtrlMode_Response):
    """Message class 'CtrlMode_Response'."""

    __slots__ = [
        '_success',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())

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


class Metaclass_CtrlMode(type):
    """Metaclass of service 'CtrlMode'."""

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
                'rei_robot_base.srv.CtrlMode')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__ctrl_mode

            from rei_robot_base.srv import _ctrl_mode
            if _ctrl_mode.Metaclass_CtrlMode_Request._TYPE_SUPPORT is None:
                _ctrl_mode.Metaclass_CtrlMode_Request.__import_type_support__()
            if _ctrl_mode.Metaclass_CtrlMode_Response._TYPE_SUPPORT is None:
                _ctrl_mode.Metaclass_CtrlMode_Response.__import_type_support__()


class CtrlMode(metaclass=Metaclass_CtrlMode):
    from rei_robot_base.srv._ctrl_mode import CtrlMode_Request as Request
    from rei_robot_base.srv._ctrl_mode import CtrlMode_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
