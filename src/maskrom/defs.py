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
import usb.core
import math

RKBINREPO = "https://github.com/rockchip-linux/rkbin"
DEFAULT_TIMEOUT = 1000
BLOCK_SIZE = 512
USB_MAX_BLOCK_COUNT = 128
USB_MAX_SECTOR_COUNT = 32
USB_MAX_TRANSFER_SIZE = BLOCK_SIZE * USB_MAX_BLOCK_COUNT
RC4_KEY = bytes([124, 78, 3, 4, 85, 5, 9, 7, 45, 44, 123, 56, 23, 13, 23, 17])
RC4_INITIAL = 0xffff
USB_TRANSFER_ALIGN = 4096

MANUFACTURER_SAMSUNG = "samsung"
MANUFACTURER_TOSHIBA = "toshiba"
MANUFACTURER_HYNIX = "hynix"
MANUFACTURER_INFINEON = "infineon"
MANUFACTURER_MICRON = "micron"
MANUFACTURER_RENESAS = "renesas"
MANUFACTURER_ST = "st"
MANUFACTURER_INTEL = "intel"
MANUFACTURER_ROCKCHIP = "rockchip"
UNKNOWN = "unknown"
UNSUPPORTED = "unsupprted"

DEVICE_RK2818 = "rk2818"
DEVICE_RK2918 = "rk2918"
DEVICE_RK2928 = "rk2928"
DEVICE_RK3026 = "rk3026"
DEVICE_RK3036 = "rk3036"
DEVICE_RK3066 = "rk3066"
DEVICE_RK3066B = "rk3066b"
DEVICE_RK3126 = "rk3126"
DEVICE_RK3128 = "rk3128"
DEVICE_RK312X = "rk312x"
DEVICE_RK3168 = "rk3168"
DEVICE_RK3188 = "rk3188"
DEVICE_RK3228 = "rk3228"
DEVICE_RK3229 = "rk3229"
DEVICE_RK322X = "rk322x"
DEVICE_RK3288 = "rk3288"
DEVICE_RK3328 = "rk3328"
DEVICE_RK3368 = "rk3368"
DEVICE_RK3399 = "rk3399"
DEVICE_RK3528 = "rk3528"
DEVICE_RK3566 = "rk3566"
DEVICE_RK3588 = "rk3588"


SOC_NAME_RK27 = "rk27"
SOC_RK28 = "rk28"
SOC_RK281X = "rk281x"
SOC_RK29 = "rk29"
SOC_RK292X = "rk292x"
SOC_RK30 = "rk30"
SOC_RK30B = "rk30b"
SOC_RK31 = "rk31"
SOC_RK32 = "rk32"
SOC_CAYMAN = "cayman"
SOC_PANDA = "panda"
SOC_SMART = "smart"
SOC_CROWN = "crown"
SOC_NANO = "nano"


CONTROL_REQUEST_TYPE_VENDOR = 0x40
CONTROL_REQUEST_LOAD = 0xc
CONTROL_INDEX_SRAM = 0x471
CONTROL_INDEX_DRAM = 0x472


FLASH_MANUFACTURERS = {0: MANUFACTURER_SAMSUNG,
                       1: MANUFACTURER_TOSHIBA,
                       2: MANUFACTURER_HYNIX,
                       3: MANUFACTURER_INFINEON,
                       4: MANUFACTURER_MICRON,
                       5: MANUFACTURER_RENESAS,
                       6: MANUFACTURER_ST,
                       7: MANUFACTURER_INTEL
                       }

RK_VENDOR_ID = 0x2207
MASKROM_VENDOR_IDS = [0x2207, 0x071b, 0x0bb4]
MASKROM_PRODUCT_IDS = {0x281a: DEVICE_RK2818,
                       0x290a: DEVICE_RK2918,
                       0x292a: DEVICE_RK2928,
                       0x292c: DEVICE_RK3026,
                       0x300a: DEVICE_RK3066,
                       0x300b: DEVICE_RK3168,
                       0x301a: DEVICE_RK3036,
                       0x310a: DEVICE_RK3066B,
                       0x310b: DEVICE_RK3188,
                       0x310c: DEVICE_RK312X,
                       0x310d: DEVICE_RK3126,
                       0x320a: DEVICE_RK3288,
                       0x320b: DEVICE_RK322X,
                       0x320c: DEVICE_RK3328,
                       0x330a: DEVICE_RK3368,
                       0x330c: DEVICE_RK3399,
                       0x350c: DEVICE_RK3528,
                       }


ROCKCHIP_SOC_TYPES = {0x10: SOC_NAME_RK27,
                      0x11: SOC_CAYMAN,
                      0x20: SOC_RK28,
                      0x21: SOC_RK281X,
                      0x22: SOC_PANDA,
                      0x30: SOC_NANO,
                      0x31: SOC_SMART,
                      0x40: SOC_CROWN,
                      0x50: SOC_RK29,
                      0x51: SOC_RK292X,
                      0x60: SOC_RK30,
                      0x61: SOC_RK30B,
                      0x70: SOC_RK31,
                      0x80: SOC_RK32,
                      }

ROCKCHIP_SOC_TAGS = {"RK27": SOC_NAME_RK27,
                     "273A": SOC_CAYMAN,
                 "281X": SOC_RK281X,
                     "282B": SOC_PANDA,
                     "290X": SOC_RK29,
                 "292X": SOC_RK292X,
                 "300A": SOC_RK30,
                 "310A": SOC_RK30B,
                 "310B": SOC_RK31,
                     "320A": SOC_RK32,
                     "262C": SOC_SMART,
                     "nano": SOC_NANO,
                     "NORC": SOC_CROWN
                     }


class MaskromException(Exception):
    pass


class LimitsException(MaskromException):
    pass


class IdbException(MaskromException):
    pass


class CommandException(MaskromException, usb.core.USBError):
    def __init__(self, strerror, error_code=None, errno=None):
        super().__init__(strerror, error_code, errno)


class PrettyInt(int):
    def __new__(cls, value, unit="B", prec=2):
        self = super(PrettyInt, cls).__new__(cls, value)
        self.unit = unit
        self.prec = prec
        return self

    def __repr__(self):
        if self == 0:
            val = 0
            multiplier = ""
        else:
            size_name = ("", "K", "M", "G", "T", "P", "E", "Z", "Y")
            i = int(math.floor(math.log(self, 1024)))
            p = math.pow(1024, i)
            val = round(self / p, self.prec)
            multiplier = size_name[i]
        return f"{val:g}{multiplier}{self.unit}"


class Printable:
    def __repr__(self):
        return ", ".join([f"{k}={getattr(self, k)}" for k in self.__dict__ if not k.startswith("_")])


def iterbatch(length, size, offset):
    factor = int(length / size)
    for _ in range(factor):
        yield offset, size
        offset += size
    if length > factor * size:
        yield offset, length - offset
