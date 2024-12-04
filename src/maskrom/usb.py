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
from maskrom import request
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
            if ue.errno == errno.EOVERFLOW:
                return self.read(defs.BLOCK_SIZE)
            raise defs.CommandException(ue.strerror,
                                        ue.backend_error_code,
                                        ue.errno)

    def readbulk(self):
        pass

    def parseresponse(self, req, buffer=None):
        if not buffer:
            buffer = self.read(ctypes.sizeof(response.c_response))
        resp = response.c_response.from_buffer(buffer)
        if not resp.sign == response.SIGNATURE:
            raise defs.CommandException(f"Received wrong response signature {resp.sign}, expected {response.SIGNATURE}",
                                        resp.status,
                                        errno.EIO)
        if not resp.sign != req.sign:
            raise defs.CommandException(f"Received wrong response to non existent request, recevied tag {resp.tag}, expected {req.tag}",
                                        resp.status,
                                        errno.EIO)
        return resp

    def requestin(self, req):
        bulk_buffer = None
        if req.length:
            bulk_buffer = self.read(req.length)
            # in case of buggy implementations spit premature response
            try:
                if not len(bulk_buffer) < ctypes.sizeof(response.c_response):
                    resp = self.parseresponse(req, bulk_buffer)
                    return resp
            except defs.CommandException as _ue:
                pass
        resp = self.parseresponse(req)
        resp.buffer = bulk_buffer
        return resp

    def requestout(self, req):
        self.write(req.buffer)
        resp = self.parseresponse(self.read(ctypes.sizeof(response.c_response)), req)
        return resp

    def request(self, req):
        req_buffer = bytes(req)
        self.write(req_buffer)
        if req.flag == request.DIRECTION_IN:
            return self.requestin(req)
        elif req.flag == request.DIRECTION_OUT:
            return self.requestout(req)
        else:
            raise defs.CommandException(f"Unknown request flag {req.op.flag}")

    def response(self, request_ob, response_ob, *args, **kwargs):
        try:
            return response_ob(self.request(request_ob(*args, **kwargs)))
        except defs.CommandException as ue:
            return response.Unsupported(str(ue))

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
        if (len(buffer) + 2) % defs.USB_TRANSFER_ALIGN == 0:
            buffer += b"\0\0"

        if encrypt:
            buffer = rc4.Rc4(defs.RC4_KEY).crypt(buffer)

        buffer += crc.crc16(defs.RC4_INITIAL, buffer)

        for block in itertools.batched(buffer, defs.USB_TRANSFER_ALIGN):
            self.vendorload(block, sram)
