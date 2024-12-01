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
import hashlib
import operator
from maskrom import defs

IDBHASH = [None, hashlib.sha256, hashlib.sha512]
IDBV2_MAGIC = b"RKNS"


class c_idbentry_v2(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("offset", ctypes.c_uint16),
        ("blocks", ctypes.c_uint16),
        ("address", ctypes.c_uint32),
        ("flag", ctypes.c_uint32),
        ("counter", ctypes.c_uint32),
        ("reserved0", ctypes.c_byte * 8),
        ("hash", ctypes.c_byte * 64),
        ]


class c_idbheader_v2(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic", ctypes.c_char * 4),
        ("reserved0", ctypes.c_byte * 4),
        ("offset", ctypes.c_uint16),
        ("numentries", ctypes.c_uint16),
        ("flags", ctypes.c_uint32),
        ("reserved1", ctypes.c_byte * 104),
        ("entries", c_idbentry_v2 * 4),
        ("reserved2", ctypes.c_byte * 1064),
        ("signature", ctypes.c_byte * 512),
        ]


def hashblock(buffer, hashtype, given=None):
    if not hashtype < len(IDBHASH):
        # signed?
        raise defs.IdbException(f"Unknown hash type {hashtype}")
    hashfunc = IDBHASH[hashtype]
    if not hashfunc:
        raise defs.IdbException(f"Unhashed idb")
        return given
    m = hashfunc()
    m.update(buffer)
    hashvalue = m.digest()
    if given:
        if hashvalue != given[:len(hashvalue)]:
            raise defs.IdbException(f"IDB hash is {given} but expected {hashvalue}")
    return hashvalue


class IdEntry(defs.Printable):
    def __init__(self, entry):
        self._entry = entry
        self.counter = self._entry.counter
        self.blocks = self._entry.blocks
        self.offset = self._entry.offset
        self.hash = bytes(self._entry.hash)
        self._blob = None

    @property
    def blob(self):
        return self._blob


class IdBlock(defs.Printable):
    @staticmethod
    def checkmagic(header):
        return header[0:4] == IDBV2_MAGIC

    def __init__(self, header):
        self.block = None
        self._idb = c_idbheader_v2.from_buffer_copy(header)
        self.hashtype = self._idb.flags & 0xf
        self.numentries = self._idb.numentries
        self.signature = hashblock(header[:-ctypes.sizeof(self._idb.signature)],
                                   self.hashtype,
                                   bytes(self._idb.signature))
        self.entries = [IdEntry(x) for x in self._idb.entries if x.counter]
        self.entries.sort(key=operator.attrgetter("counter"))

    def read(self, f):
        self.block = int((f.tell() - ctypes.sizeof(c_idbheader_v2)) / defs.BLOCK_SIZE)
        for entry in self.entries:
            f.seek((self.block + entry.offset) * defs.BLOCK_SIZE)
            entry._blob = f.read(entry.blocks * defs.BLOCK_SIZE)
            entry.hash = hashblock(entry._blob, self.hashtype, bytes(entry.hash))


def iteridbs(f):
    while True:
        block = f.read(defs.BLOCK_SIZE)
        if not block:
            break
        if IdBlock.checkmagic(block):
            block += f.read(defs.BLOCK_SIZE * 3)
            try:
                idblock = IdBlock(block)
                idblock.read(f)
            except defs.IdbException as e:
                continue
                # print(int(f.tell()) / defs.BLOCK_SIZE, e)
            print("found idb:", idblock)
