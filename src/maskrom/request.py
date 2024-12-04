"""
 Copyright (C) 2024 boogie

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import ctypes
import random
from maskrom import op
from maskrom import defs

SIGNATURE = b"USBC"
DIRECTION_OUT = 0
DIRECTION_IN = 128

SECTOR_SIZE = 512
OOB_SIZE = 16


class c_request(ctypes.BigEndianStructure):
    buffer = None
    _pack_ = 1
    _fields_ = [
            ('sign', ctypes.c_char * 4),
            ('tag', ctypes.c_uint32),
            ('length', ctypes.c_uint32),
            ('flag', ctypes.c_uint8),
            ('lun', ctypes.c_uint8),
            ('cblen', ctypes.c_uint8),
            ('op', op.c_rkusbop),
            ]


def gettag():
    return random.randint(0, 2 ** 32)


def test_unit_ready():
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=6,
                     op=op.test_unit_ready())


def read_flash_id():
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, length=5, cblen=6,
                     op=op.read_flash_id())


def write_sector(pos, count):
    if count > defs.USB_MAX_SECTOR_COUNT:
        raise defs.LimitsException(f"Maximum allowed number of sectors to read is {defs.USB_MAX_SECTOR_COUNT} but {count} given")

    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_OUT, cblen=10, length=count * (SECTOR_SIZE + OOB_SIZE),
                     op=op.write_sector(address=pos, length=count))


def read_sector(pos, count):
    if count > defs.USB_MAX_SECTOR_COUNT:
        raise defs.LimitsException(f"Maximum allowed number of sectors to read is {defs.USB_MAX_SECTOR_COUNT} but {count} given")

    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=10, length=count * (SECTOR_SIZE + OOB_SIZE),
                     op=op.read_sector(address=pos, length=count))


def read_lba(pos, count):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=10, length=count * SECTOR_SIZE,
                     op=op.read_lba(address=pos, length=count))


def read_sdram(pos, size):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=10, length=size,
                     op=op.read_sdram(address=pos, size=size))


def write_sdram(pos, size):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_OUT, cblen=10, length=size,
                     op=op.write_sdram(address=pos, size=size))


def execute_sdram(pos):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_OUT, cblen=10,
                     op=op.execute_sdram(address=pos))


def write_lba(pos, count):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_OUT, cblen=10, length=count * SECTOR_SIZE,
                     op=op.write_lba(address=pos, length=count))


def read_flash_info():
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=6, length=defs.USB_MAX_TRANSFER_SIZE,
                     op=op.read_flash_info())


def read_chip_info():
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=6, length=16,
                     op=op.read_chip_info())


def erase_lba(pos, count):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_OUT, cblen=10,
                     op=op.erase_lba(address=pos, length=count))


def read_capability():
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=6, length=8,
                     op=op.read_capability())


def device_reset(subcode):
    return c_request(sign=SIGNATURE, tag=gettag(),
                     flag=DIRECTION_IN, cblen=6,
                     op=op.device_reset(subcode))
