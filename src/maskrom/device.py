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

import itertools

from maskrom import request
from maskrom import response
from maskrom import usb
from maskrom import defs


class Device:
    def __init__(self, offset=0, timeout=defs.DEFAULT_TIMEOUT):
        self.usb = usb.Usb(offset, timeout)

    def flush(self):
        try:
            self.usb.read(defs.BLOCK_SIZE)
        except defs.MaskromException:
            pass

    def load_sram(self, path, encrypt=True):
        return self.usb.loadfiletoram(path, True, encrypt)

    def load_dram(self, path, encrypt=True):
        return self.usb.loadfiletoram(path, False, encrypt)

    def read_flash_id(self):
        # TODO: emmc: 0x434d4d45: EMMC
        return self.usb.response(request.read_flash_id, response.FlashId)

    def read_flash_info(self):
        return self.usb.response(request.read_flash_info, response.FlashInfo)

    def read_chip_info(self):
        return self.usb.response(request.read_chip_info, response.ChipInfo)

    def test_unit_ready(self):
        return self.usb.response(request.test_unit_ready, response.Status)

    def read_capability(self):
        return self.usb.response(request.read_capability, response.Capability)

    def device_reset(self, subcode=0):
        return self.usb.response(request.device_reset, response.Status, subcode)

    def iter_lba(self, offset, length):
        for offset, size in defs.iterbatch(length, defs.USB_MAX_BLOCK_COUNT, offset):
            yield self.usb.response(request.read_lba, response.Buffer, offset, size)

    def iter_sector(self, offset, length):
        for offset, size in defs.iterbatch(length, defs.USB_MAX_SECTOR_COUNT, offset):
            yield self.usb.response(request.read_sector, response.Buffer, offset, size)

    def iter_ram(self, offset, size):
        for offset, size in defs.iterbatch(size, defs.USB_MAX_TRANSFER_SIZE, offset):
            yield self.usb.response(request.read_sdram, response.Buffer, offset, size)

    # def write_ram(self, offset, buffer):
    #     for chunk in itertools.batched(buffer, defs.USB_MAX_TRANSFER_SIZE):
    #        yield self.usb.response(request.write_sdram, bytes, offset, size)
