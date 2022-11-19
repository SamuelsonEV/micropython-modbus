#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# system packages
import struct

# custom packages
from . import const as Const

# typing not natively supported on MicroPython
from .typing import List, Union


def read_coils(starting_address: int, quantity: int) -> bytes:
    """
    Create Modbus Protocol Data Unit for reading coils.

    :param      starting_address:  The starting address
    :type       starting_address:  int
    :param      quantity:          Quantity of coils
    :type       quantity:          int

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    if not (1 <= quantity <= 2000):
        raise ValueError('Invalid number of coils')

    return struct.pack('>BHH', Const.READ_COILS, starting_address, quantity)


def read_discrete_inputs(starting_address: int, quantity: int) -> bytes:
    """
    Create Modbus Protocol Data Unit for reading discrete inputs.

    :param      starting_address:  The starting address
    :type       starting_address:  int
    :param      quantity:          Quantity of coils
    :type       quantity:          int

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    if not (1 <= quantity <= 2000):
        raise ValueError('Invalid number of discrete inputs')

    return struct.pack('>BHH',
                       Const.READ_DISCRETE_INPUTS,
                       starting_address,
                       quantity)


def read_holding_registers(starting_address: int, quantity: int) -> bytes:
    """
    Create Modbus Protocol Data Unit for reading holding registers.

    :param      starting_address:  The starting address
    :type       starting_address:  int
    :param      quantity:          Quantity of coils
    :type       quantity:          int

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    if not (1 <= quantity <= 125):
        raise ValueError('Invalid number of holding registers')

    return struct.pack('>BHH',
                       Const.READ_HOLDING_REGISTERS,
                       starting_address,
                       quantity)


def read_input_registers(starting_address: int, quantity: int) -> bytes:
    """
    Create Modbus Protocol Data Unit for reading input registers.

    :param      starting_address:  The starting address
    :type       starting_address:  int
    :param      quantity:          Quantity of coils
    :type       quantity:          int

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    if not (1 <= quantity <= 125):
        raise ValueError('Invalid number of input registers')

    return struct.pack('>BHH',
                       Const.READ_INPUT_REGISTER,
                       starting_address,
                       quantity)


def write_single_coil(output_address: int,
                      output_value: Union[int, bool]) -> bytes:
    """
    Create Modbus message to update single coil

    :param      output_address:  The output address
    :type       output_address:  int
    :param      output_value:    The output value
    :type       output_value:    Union[int, bool]

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    if output_value not in [0x0000, 0xFF00, True]:
        raise ValueError('Illegal coil value')

    if output_value not in [0x0000, 0xFF00]:
        if output_value:
            output_value = 0xFF00
        else:
            output_value = 0x0000

    return struct.pack('>BHH',
                       Const.WRITE_SINGLE_COIL,
                       output_address,
                       output_value)


def write_single_register(register_address: int,
                          register_value: int,
                          signed=True) -> bytes:
    """
    Create Modbus message to writes a single register

    :param      register_address:  The register address
    :type       register_address:  int
    :param      register_value:    The register value
    :type       register_value:    int
    :param      signed:            Flag whether data is signed or not
    :type       signed:            bool

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    fmt = 'h' if signed else 'H'

    return struct.pack('>BH' + fmt,
                       Const.WRITE_SINGLE_REGISTER,
                       register_address,
                       register_value)


def write_multiple_coils(starting_address: int,
                         value_list: List[int, bool]) -> bytes:
    """
    Create Modbus message to update multiple coils

    :param      starting_address:  The starting address
    :type       starting_address:  int
    :param      value_list:        The list of output values
    :type       value_list:        List[int, bool]

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    if not (1 <= len(value_list) <= 0x07B0):
        raise ValueError('Invalid quantity of outputs')

    sectioned_list = [value_list[i:i + 8] for i in range(0, len(value_list), 8)]    # noqa: E501

    output_value = []
    for index, byte in enumerate(sectioned_list):
        # see https://github.com/brainelectronics/micropython-modbus/issues/22
        # output = sum(v << i for i, v in enumerate(byte))
        output = 0
        for bit in byte:
            output = (output << 1) | bit
        output_value.append(output)

    fmt = 'B' * len(output_value)

    return struct.pack('>BHHB' + fmt,
                       Const.WRITE_MULTIPLE_COILS,
                       starting_address,
                       len(value_list),     # quantity of outputs
                       ((len(value_list) - 1) // 8) + 1,    # byte count
                       *output_value)


def write_multiple_registers(starting_address: int,
                             register_values: List[int],
                             signed=True):
    """
    Create Modbus message to update multiple coils

    :param      starting_address:  The starting address
    :type       starting_address:  int
    :param      register_values:   The list of output value
    :type       register_values:   List[int, bool]
    :param      signed:            Flag whether data is signed or not
    :type       signed:            bool

    :returns:   Packed Modbus message
    :rtype:     bytes
    """
    quantity = len(register_values)

    if not (1 <= quantity <= 123):
        raise ValueError('Invalid number of registers')

    fmt = ('h' if signed else 'H') * quantity
    return struct.pack('>BHHB' + fmt,
                       Const.WRITE_MULTIPLE_REGISTERS,
                       starting_address,
                       quantity,
                       quantity * 2,
                       *register_values)


def validate_resp_data(data: bytes,
                       function_code: int,
                       address: int,
                       value: int = None,
                       quantity: int = None,
                       signed: bool = True) -> bool:
    """
    Validate the response data.

    :param      data:           The data
    :type       data:           bytes
    :param      function_code:  The function code
    :type       function_code:  int
    :param      address:        The address
    :type       address:        int
    :param      value:          The value
    :type       value:          int
    :param      quantity:       The quantity
    :type       quantity:       int
    :param      signed:         Indicates if signed
    :type       signed:         bool

    :returns:   True if valid, False otherwise
    :rtype:     bool
    """
    fmt = '>H' + ('h' if signed else 'H')

    if function_code in [Const.WRITE_SINGLE_COIL, Const.WRITE_SINGLE_REGISTER]:
        resp_addr, resp_value = struct.unpack(fmt, data)

        if (address == resp_addr) and (value == resp_value):
            return True
    elif function_code in [Const.WRITE_MULTIPLE_COILS,
                           Const.WRITE_MULTIPLE_REGISTERS]:
        resp_addr, resp_qty = struct.unpack(fmt, data)

        if (address == resp_addr) and (quantity == resp_qty):
            return True

    return False


def response(function_code: int,
             request_register_addr: int,
             request_register_qty: int,
             request_data,
             value_list=None,
             signed=True):
    if function_code in [Const.READ_COILS, Const.READ_DISCRETE_INPUTS]:
        sectioned_list = [value_list[i:i + 8] for i in range(0, len(value_list), 8)]    # noqa: E501

        output_value = []
        for index, byte in enumerate(sectioned_list):
            # see https://github.com/brainelectronics/micropython-modbus/issues/22
            # output = sum(v << i for i, v in enumerate(byte))
            output = 0
            for bit in byte:
                output = (output << 1) | bit
            output_value.append(output)

        fmt = 'B' * len(output_value)
        return struct.pack('>BB' + fmt,
                           function_code,
                           ((len(value_list) - 1) // 8) + 1,
                           *output_value)

    elif function_code in [Const.READ_HOLDING_REGISTERS,
                           Const.READ_INPUT_REGISTER]:
        quantity = len(value_list)

        if not (0x0001 <= quantity <= 0x007D):
            raise ValueError('invalid number of registers')

        if signed is True or signed is False:
            fmt = ('h' if signed else 'H') * quantity
        else:
            fmt = ''
            for s in signed:
                fmt += 'h' if s else 'H'

        return struct.pack('>BB' + fmt,
                           function_code,
                           quantity * 2,
                           *value_list)

    elif function_code in [Const.WRITE_SINGLE_COIL,
                           Const.WRITE_SINGLE_REGISTER]:
        return struct.pack('>BHBB',
                           function_code,
                           request_register_addr,
                           *request_data)

    elif function_code in [Const.WRITE_MULTIPLE_COILS,
                           Const.WRITE_MULTIPLE_REGISTERS]:
        return struct.pack('>BHH',
                           function_code,
                           request_register_addr,
                           request_register_qty)


def exception_response(function_code: int, exception_code: int) -> bytes:
    return struct.pack('>BB', Const.ERROR_BIAS + function_code, exception_code)


def float_to_bin(num: float) -> bin:
    return bin(struct.unpack('!I', struct.pack('!f', num))[0])[2:].zfill(32)


def bin_to_float(binary: bin) -> float:
    return struct.unpack('!f', struct.pack('!I', int(binary, 2)))[0]


def int_to_bin(num: int) -> str:
    return "{0:b}".format(num)
