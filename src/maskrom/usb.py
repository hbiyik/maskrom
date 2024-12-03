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
import errno
import itertools
import usb.util

from maskrom import crc
from maskrom import defs
from maskrom import rc4
from maskrom import response


def iterdevices():
    for dev in usb.core.find(find_all=True):
        if dev.idVendor in defs.MASKROM_VENDOR_IDS:
            yield dev


class Usb:
    def __init__(self, offset=0, timeout=defs.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.dev = list(iterdevices())[offset]
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0, 0)]
        self.ep_write = usb.util.find_descriptor(intf, custom_match=self.find_ep_out)
        self.ep_read = usb.util.find_descriptor(intf, custom_match=self.find_ep_in)

    def find_ep_in(self, e):
        return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN

    def find_ep_out(self, e):
        return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT

    def write(self, buffer, timeout=None):
        timeout = timeout or self.timeout
        try:
            return self.ep_write.write(buffer, timeout=timeout)
        except usb.core.USBError as ue:
            raise defs.CommandException(ue.strerror,
                                        ue.backend_error_code,
                                        ue.errno)

    def read(self, size, timeout=None):
        timeout = timeout or self.timeout
        try:
            return self.ep_read.read(size, timeout=timeout)
        except usb.core.USBError as ue:
            raise defs.CommandException(ue.strerror,
                                        ue.backend_error_code,
                                        ue.errno)

    def request(self, req):
        req_buffer = bytes(req)
        try:
            self.write(req_buffer)
        except defs.CommandException as e:
            if e.errno == errno.EIO:
                return response.Unsupported()
        retval = True
        if req.length:
            retval = self.read(max(min(defs.USB_MAX_BLOCK_SIZE, req.length), req.length))
            # check first if invalid response is provided
            respsize = ctypes.sizeof(response.c_response)
            if len(retval) >= respsize:
                first_resp = response.c_response.from_buffer(retval[:respsize])
                if first_resp.sign == response.SIGNATURE and first_resp.tag == req.tag:
                    if first_resp.status != response.STATUS_OK:
                        return response.Unsupported()
                    return True
        resp_buffer = self.read(min(defs.USB_MAX_BLOCK_SIZE, ctypes.sizeof(response.c_response)))
        resp = response.c_response.from_buffer(resp_buffer)
        if not resp.sign == response.SIGNATURE:
            raise defs.CommandException(f"Received wrong response signature {resp.sign}, expected {response.SIGNATURE}",
                                        resp.status,
                                        errno.EIO)
        if not resp.sign != req.sign:
            raise defs.CommandException(f"Received wrong response to non existent request, recevied tag {resp.tag}, expected {req.tag}",
                                        resp.status,
                                        errno.EIO)
        if resp.status != response.STATUS_OK:
            return False
        return retval

    def response(self, request_ob, response_ob, *args, **kwargs):
        retval = self.request(request_ob(*args, **kwargs))
        if response_ob and isinstance(retval, bool):
            retval = response.Unsupported()
        if not response_ob or isinstance(retval, response.Unsupported):
            return retval
        else:
            return response_ob(retval)

    def vendorload(self, buffer, sram=True):
        return self.dev.ctrl_transfer(defs.CONTROL_REQUEST_TYPE_VENDOR,
                                      defs.CONTROL_REQUEST_LOAD,
                                      0,
                                      defs.CONTROL_INDEX_SRAM if sram else defs.CONTROL_INDEX_DRAM,
                                      buffer)

    def loadfiletoram(self, fpath, sram=True, encrypt=True):
        with open(fpath, "rb") as f:
            buffer = f.read()
        # transfer is finished when last unaligned block is sent
        # if file-size + 2 byte crc is block aligned, send an extra 0x00 padding to
        # un-align the total transfer size and finish the transfer
        if (len(buffer) + 2) % defs.USB_TRANSFER_BLOCKSIZE == 0:
            buffer += b"\0\0"

        if encrypt:
            buffer = rc4.Rc4(defs.RC4_KEY).crypt(buffer)

        buffer += crc.crc16(defs.RC4_INITIAL, buffer)

        for block in itertools.batched(buffer, defs.USB_TRANSFER_BLOCKSIZE):
            self.vendorload(block, sram)
