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
import datetime
from maskrom import defs

SIGNATURE = b"USBS"
STATUS_OK = 0
STATUS_FAIL = 1


class c_response(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('sign', ctypes.c_char * 4),
        ('tag', ctypes.c_uint32),
        ('residue', ctypes.c_uint32),
        ('status', ctypes.c_int8)]


class c_flashinfo(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('flashsize', ctypes.c_uint),
        ('blocksize', ctypes.c_uint16),
        ('pagesize', ctypes.c_uint8),
        ('ecc', ctypes.c_uint8),
        ('accesstime', ctypes.c_uint8),
        ('manufacturer', ctypes.c_uint8),
        ('chipselect', ctypes.c_uint8),
        ]


class c_chipinfo(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('tag', ctypes.c_char * 4),
        ('year', ctypes.c_char * 4),
        ('month', ctypes.c_char * 2),
        ('day', ctypes.c_char * 2),
        ('revision', ctypes.c_char * 4),
        ]


class FlashId(defs.Printable):
    def __init__(self, buffer):
        self.id = bytes(buffer).decode()


class ChipInfo(defs.Printable):
    def __init__(self, buffer):
        buflen = ctypes.sizeof(c_chipinfo)
        self.__chipinfo = c_chipinfo.from_buffer(buffer[:buflen])
        self._reserved = buffer[buflen:]
        self.tag = self.__chipinfo.tag[::-1].decode()
        try:
            year = int(self.__chipinfo.year[::-1])
            month = int(self.__chipinfo.month)
            day = int(self.__chipinfo.day)
            self.date = datetime.datetime(year, month, day)
        except ValueError:
            self.day = bytes(self.__chipinfo.day)
            self.moth = bytes(self.__chipinfo.month)
            self.date = bytes(self.__chipinfo.year)
        try:
            self.revision = self.__chipinfo.revision[::-1].decode()
        except ValueError:
            self.revision = self.__chipinfo.revision[::-1]
        self.socid = defs.ROCKCHIP_SOC_TAGS.get(self.tag, defs.UNKNOWN)


class FlashInfo(defs.Printable):
    def __init__(self, buffer, numchips=2):
        infolen = ctypes.sizeof(c_flashinfo)
        self.__flashinfo = c_flashinfo.from_buffer(buffer[:infolen])
        self._reserved = buffer[infolen:]
        # convert to bytes
        self.numchips = numchips
        self.flashsize = defs.PrettyInt(self.__flashinfo.flashsize * 1024 / numchips)
        self.blocksize = defs.PrettyInt(self.__flashinfo.blocksize * 1024 / numchips)
        self.blocknum = int(self.flashsize / self.blocksize)
        self.pagesize = defs.PrettyInt(self.__flashinfo.pagesize * 1024 / numchips)
        self.sectorperblock = int(self.blocksize / self.pagesize)
        self.ecc = defs.PrettyInt(self.__flashinfo.ecc, "b")
        self.acccesstime = self.__flashinfo.accesstime
        self.manufacturer = self.__flashinfo.manufacturer
        self.manufacturername = defs.FLASH_MANUFACTURERS.get(self.manufacturer, defs.UNKNOWN)
        self.chipselect = self.__flashinfo.chipselect


class Capability(defs.Printable):
    def __init__(self, buffer):
        if len(buffer) < 8:
            return ValueError(f"Unexpected buffer length for capability, expected 8 received {len(buffer)}")
        self.__buffer = buffer
        self.direct_lba = bool(buffer[0] & (1 << 0))
        self.vendor_storage = bool(buffer[0] & (1 << 1))
        self.first_4Mb_maccess = bool(buffer[0] & (1 << 2))
        self.read_lba = bool(buffer[0] & (1 << 3))
        self.new_vendors_torage = bool(buffer[0] & (1 << 4))
        self.read_com_log = bool(buffer[0] & (1 << 5))
        self.read_idb_config = bool(buffer[0] & (1 << 6))
        self.read_secure_mode = bool(buffer[0] & (1 << 7))
        self.new_idb = bool(buffer[1] & (1 << 0))
        self.switch_storage = bool(buffer[1] & (1 << 1))
        self.lba_parity = bool(buffer[1] & (1 << 2))
        self.read_otp_chip = bool(buffer[1] & (1 << 3))
        self.switch_usb3 = bool(buffer[1] & (1 << 4))


class Unsupported:
    def __repr__(self):
        return "unsupported"
