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


class c_rkusbop(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
            ('code', ctypes.c_uint8),
            ('subcode', ctypes.c_uint8),
            ('address', ctypes.c_uint32),
            ('res1', ctypes.c_uint8),
            ('length', ctypes.c_uint16),
            ('res1', ctypes.c_uint8 * 7),
            ]


def test_unit_ready():
    return c_rkusbop(code=0)


def read_flash_id():
    return c_rkusbop(code=1)


def write_sector(address, length):
    return c_rkusbop(code=5, address=address, length=length)


def read_lba(address, length, lbamethod=False):
    return c_rkusbop(code=20, subcode=int(lbamethod), address=address, length=length)


def write_lba(address, length, lbamethod=False):
    return c_rkusbop(code=21, subcode=int(lbamethod), address=address, length=length)


def read_flash_info():
    return c_rkusbop(code=26)


def read_chip_info():
    return c_rkusbop(code=27)


def erase_lba(address, length):
    return c_rkusbop(code=37, address=address, length=length)


def read_capability():
    return c_rkusbop(code=170)


def device_reset(subcode):
    return c_rkusbop(code=255, subcode=subcode)


# below op codes are not exactly known, reference: rkdeveloptool
def test_bad_block(subcode=0, address=0, length=0):
    return c_rkusbop(code=3, subcode=subcode, address=address, length=length)


def read_sector(address=0, length=0):
    return c_rkusbop(code=4, subcode=0, address=address, length=length)


def erase_normal(subcode=0, address=0, length=0):
    return c_rkusbop(code=6, subcode=subcode, address=address, length=length)


def erase_force(subcode=0, address=0, length=0):
    return c_rkusbop(code=11, subcode=subcode, address=address, length=length)


def erase_systemdisk(subcode=0, address=0, length=0):
    return c_rkusbop(code=22, subcode=subcode, address=address, length=length)


def read_sdram(subcode=0, address=0, length=0):
    return c_rkusbop(code=23, subcode=subcode, address=address, length=length)


def write_sdram(subcode=0, address=0, length=0):
    return c_rkusbop(code=24, subcode=subcode, address=address, length=length)


def execute_sdram(subcode=0, address=0, length=0):
    return c_rkusbop(code=25, subcode=subcode, address=address, length=length)


def set_reset_flag(subcode=0, address=0, length=0):
    return c_rkusbop(code=30, subcode=subcode, address=address, length=length)


def write_efuse(subcode=0, address=0, length=0):
    return c_rkusbop(code=31, subcode=subcode, address=address, length=length)


def read_efuse(subcode=0, address=0, length=0):
    return c_rkusbop(code=32, subcode=subcode, address=address, length=length)


def read_spi_flash(subcode=0, address=0, length=0):
    return c_rkusbop(code=33, subcode=subcode, address=address, length=length)


def write_spi_flash(subcode=0, address=0, length=0):
    return c_rkusbop(code=34, subcode=subcode, address=address, length=length)


def write_new_efuse(subcode=0, address=0, length=0):
    return c_rkusbop(code=35, subcode=subcode, address=address, length=length)


def read_new_efuse(subcode=0, address=0, length=0):
    return c_rkusbop(code=36, subcode=subcode, address=address, length=length)
