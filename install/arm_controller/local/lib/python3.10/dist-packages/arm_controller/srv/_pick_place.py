# generated from rosidl_generator_py/resource/_idl.py.em
# with input from arm_controller:srv/PickPlace.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_PickPlace_Request(type):
    """Metaclass of message 'PickPlace_Request'."""

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
            module = import_type_support('arm_controller')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'arm_controller.srv.PickPlace_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__pick_place__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__pick_place__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__pick_place__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__pick_place__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__pick_place__request

            from arm_controller.msg import Control
            if Control.__class__._TYPE_SUPPORT is None:
                Control.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class PickPlace_Request(metaclass=Metaclass_PickPlace_Request):
    """Message class 'PickPlace_Request'."""

    __slots__ = [
        '_number',
        '_mode',
        '_pose',
    ]

    _fields_and_field_types = {
        'number': 'uint8',
        'mode': 'uint8',
        'pose': 'arm_controller/Control',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['arm_controller', 'msg'], 'Control'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.number = kwargs.get('number', int())
        self.mode = kwargs.get('mode', int())
        from arm_controller.msg import Control
        self.pose = kwargs.get('pose', Control())

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
        if self.number != other.number:
            return False
        if self.mode != other.mode:
            return False
        if self.pose != other.pose:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def number(self):
        """Message field 'number'."""
        return self._number

    @number.setter
    def number(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'number' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'number' field must be an unsigned integer in [0, 255]"
        self._number = value

    @builtins.property
    def mode(self):
        """Message field 'mode'."""
        return self._mode

    @mode.setter
    def mode(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'mode' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'mode' field must be an unsigned integer in [0, 255]"
        self._mode = value

    @builtins.property
    def pose(self):
        """Message field 'pose'."""
        return self._pose

    @pose.setter
    def pose(self, value):
        if __debug__:
            from arm_controller.msg import Control
            assert \
                isinstance(value, Control), \
                "The 'pose' field must be a sub message of type 'Control'"
        self._pose = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_PickPlace_Response(type):
    """Metaclass of message 'PickPlace_Response'."""

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
            module = import_type_support('arm_controller')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'arm_controller.srv.PickPlace_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__pick_place__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__pick_place__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__pick_place__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__pick_place__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__pick_place__response

            from arm_controller.msg import Control
            if Control.__class__._TYPE_SUPPORT is None:
                Control.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class PickPlace_Response(metaclass=Metaclass_PickPlace_Response):
    """Message class 'PickPlace_Response'."""

    __slots__ = [
        '_pose',
        '_success',
        '_message',
    ]

    _fields_and_field_types = {
        'pose': 'arm_controller/Control',
        'success': 'boolean',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['arm_controller', 'msg'], 'Control'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from arm_controller.msg import Control
        self.pose = kwargs.get('pose', Control())
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
        if self.pose != other.pose:
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
    def pose(self):
        """Message field 'pose'."""
        return self._pose

    @pose.setter
    def pose(self, value):
        if __debug__:
            from arm_controller.msg import Control
            assert \
                isinstance(value, Control), \
                "The 'pose' field must be a sub message of type 'Control'"
        self._pose = value

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


class Metaclass_PickPlace(type):
    """Metaclass of service 'PickPlace'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('arm_controller')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'arm_controller.srv.PickPlace')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__pick_place

            from arm_controller.srv import _pick_place
            if _pick_place.Metaclass_PickPlace_Request._TYPE_SUPPORT is None:
                _pick_place.Metaclass_PickPlace_Request.__import_type_support__()
            if _pick_place.Metaclass_PickPlace_Response._TYPE_SUPPORT is None:
                _pick_place.Metaclass_PickPlace_Response.__import_type_support__()


class PickPlace(metaclass=Metaclass_PickPlace):
    from arm_controller.srv._pick_place import PickPlace_Request as Request
    from arm_controller.srv._pick_place import PickPlace_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
