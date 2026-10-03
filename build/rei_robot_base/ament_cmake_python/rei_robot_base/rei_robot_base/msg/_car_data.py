# generated from rosidl_generator_py/resource/_idl.py.em
# with input from rei_robot_base:msg/CarData.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'motor_speed'
# Member 'crash'
# Member 'cliff'
# Member 'ultrasound'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

# Member 'input_io'
# Member 'output_io'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_CarData(type):
    """Metaclass of message 'CarData'."""

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
                'rei_robot_base.msg.CarData')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__car_data
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__car_data
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__car_data
            cls._TYPE_SUPPORT = module.type_support_msg__msg__car_data
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__car_data

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class CarData(metaclass=Metaclass_CarData):
    """Message class 'CarData'."""

    __slots__ = [
        '_header',
        '_motor_speed',
        '_crash',
        '_cliff',
        '_ultrasound',
        '_smoke',
        '_power_voltage',
        '_is_charge',
        '_tempareture',
        '_relative_humidity',
        '_input_io',
        '_output_io',
        '_relay_status',
        '_connect_status',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'motor_speed': 'sequence<double>',
        'crash': 'sequence<int8>',
        'cliff': 'sequence<int8>',
        'ultrasound': 'sequence<float>',
        'smoke': 'int8',
        'power_voltage': 'float',
        'is_charge': 'boolean',
        'tempareture': 'float',
        'relative_humidity': 'float',
        'input_io': 'int8[4]',
        'output_io': 'int8[7]',
        'relay_status': 'boolean',
        'connect_status': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('double')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('int8'), 4),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('int8'), 7),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.motor_speed = array.array('d', kwargs.get('motor_speed', []))
        self.crash = array.array('b', kwargs.get('crash', []))
        self.cliff = array.array('b', kwargs.get('cliff', []))
        self.ultrasound = array.array('f', kwargs.get('ultrasound', []))
        self.smoke = kwargs.get('smoke', int())
        self.power_voltage = kwargs.get('power_voltage', float())
        self.is_charge = kwargs.get('is_charge', bool())
        self.tempareture = kwargs.get('tempareture', float())
        self.relative_humidity = kwargs.get('relative_humidity', float())
        if 'input_io' not in kwargs:
            self.input_io = numpy.zeros(4, dtype=numpy.int8)
        else:
            self.input_io = numpy.array(kwargs.get('input_io'), dtype=numpy.int8)
            assert self.input_io.shape == (4, )
        if 'output_io' not in kwargs:
            self.output_io = numpy.zeros(7, dtype=numpy.int8)
        else:
            self.output_io = numpy.array(kwargs.get('output_io'), dtype=numpy.int8)
            assert self.output_io.shape == (7, )
        self.relay_status = kwargs.get('relay_status', bool())
        self.connect_status = kwargs.get('connect_status', bool())

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
        if self.header != other.header:
            return False
        if self.motor_speed != other.motor_speed:
            return False
        if self.crash != other.crash:
            return False
        if self.cliff != other.cliff:
            return False
        if self.ultrasound != other.ultrasound:
            return False
        if self.smoke != other.smoke:
            return False
        if self.power_voltage != other.power_voltage:
            return False
        if self.is_charge != other.is_charge:
            return False
        if self.tempareture != other.tempareture:
            return False
        if self.relative_humidity != other.relative_humidity:
            return False
        if all(self.input_io != other.input_io):
            return False
        if all(self.output_io != other.output_io):
            return False
        if self.relay_status != other.relay_status:
            return False
        if self.connect_status != other.connect_status:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def motor_speed(self):
        """Message field 'motor_speed'."""
        return self._motor_speed

    @motor_speed.setter
    def motor_speed(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'd', \
                "The 'motor_speed' array.array() must have the type code of 'd'"
            self._motor_speed = value
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
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -1.7976931348623157e+308 or val > 1.7976931348623157e+308) or math.isinf(val) for val in value)), \
                "The 'motor_speed' field must be a set or sequence and each value of type 'float' and each double in [-179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000, 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000]"
        self._motor_speed = array.array('d', value)

    @builtins.property
    def crash(self):
        """Message field 'crash'."""
        return self._crash

    @crash.setter
    def crash(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'b', \
                "The 'crash' array.array() must have the type code of 'b'"
            self._crash = value
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
                "The 'crash' field must be a set or sequence and each value of type 'int' and each integer in [-128, 127]"
        self._crash = array.array('b', value)

    @builtins.property
    def cliff(self):
        """Message field 'cliff'."""
        return self._cliff

    @cliff.setter
    def cliff(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'b', \
                "The 'cliff' array.array() must have the type code of 'b'"
            self._cliff = value
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
                "The 'cliff' field must be a set or sequence and each value of type 'int' and each integer in [-128, 127]"
        self._cliff = array.array('b', value)

    @builtins.property
    def ultrasound(self):
        """Message field 'ultrasound'."""
        return self._ultrasound

    @ultrasound.setter
    def ultrasound(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'ultrasound' array.array() must have the type code of 'f'"
            self._ultrasound = value
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
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'ultrasound' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._ultrasound = array.array('f', value)

    @builtins.property
    def smoke(self):
        """Message field 'smoke'."""
        return self._smoke

    @smoke.setter
    def smoke(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'smoke' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'smoke' field must be an integer in [-128, 127]"
        self._smoke = value

    @builtins.property
    def power_voltage(self):
        """Message field 'power_voltage'."""
        return self._power_voltage

    @power_voltage.setter
    def power_voltage(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'power_voltage' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'power_voltage' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._power_voltage = value

    @builtins.property
    def is_charge(self):
        """Message field 'is_charge'."""
        return self._is_charge

    @is_charge.setter
    def is_charge(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'is_charge' field must be of type 'bool'"
        self._is_charge = value

    @builtins.property
    def tempareture(self):
        """Message field 'tempareture'."""
        return self._tempareture

    @tempareture.setter
    def tempareture(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'tempareture' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'tempareture' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._tempareture = value

    @builtins.property
    def relative_humidity(self):
        """Message field 'relative_humidity'."""
        return self._relative_humidity

    @relative_humidity.setter
    def relative_humidity(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'relative_humidity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'relative_humidity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._relative_humidity = value

    @builtins.property
    def input_io(self):
        """Message field 'input_io'."""
        return self._input_io

    @input_io.setter
    def input_io(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.int8, \
                "The 'input_io' numpy.ndarray() must have the dtype of 'numpy.int8'"
            assert value.size == 4, \
                "The 'input_io' numpy.ndarray() must have a size of 4"
            self._input_io = value
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
                 len(value) == 4 and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -128 and val < 128 for val in value)), \
                "The 'input_io' field must be a set or sequence with length 4 and each value of type 'int' and each integer in [-128, 127]"
        self._input_io = numpy.array(value, dtype=numpy.int8)

    @builtins.property
    def output_io(self):
        """Message field 'output_io'."""
        return self._output_io

    @output_io.setter
    def output_io(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.int8, \
                "The 'output_io' numpy.ndarray() must have the dtype of 'numpy.int8'"
            assert value.size == 7, \
                "The 'output_io' numpy.ndarray() must have a size of 7"
            self._output_io = value
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
                 len(value) == 7 and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -128 and val < 128 for val in value)), \
                "The 'output_io' field must be a set or sequence with length 7 and each value of type 'int' and each integer in [-128, 127]"
        self._output_io = numpy.array(value, dtype=numpy.int8)

    @builtins.property
    def relay_status(self):
        """Message field 'relay_status'."""
        return self._relay_status

    @relay_status.setter
    def relay_status(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'relay_status' field must be of type 'bool'"
        self._relay_status = value

    @builtins.property
    def connect_status(self):
        """Message field 'connect_status'."""
        return self._connect_status

    @connect_status.setter
    def connect_status(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'connect_status' field must be of type 'bool'"
        self._connect_status = value
