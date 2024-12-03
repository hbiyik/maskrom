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
from maskrom import defs

LEGACY_COMMIT = "d24503d2bd236780d36bff9243b1a4557d38ec30"
LATEST_COMMIT = "7c35e21a8529b3758d1f051d1a5dc62aae934b2b"


class RkBin:
    def __init__(self, *variants):
        self.variants = variants


class RkBinOfficial(RkBin):
    def __init__(self, commit, *variants):
        _variants = {}
        for k, v in variants.items():
            _variants[k] = f"{defs.RKBINREPO}/raw/{commit}/{v}"
        super().__init__(**_variants)


def rkbin(commit, path):
    return f"{defs.RKBINREPO}/raw/{commit}/{path}"


class RockchipSoc:
    vid = defs.RK_VENDOR_ID
    pid = None
    sram = {}
    dram = {}
    tag = None


class Rk1106(RockchipSoc):
    pid = 0x110c


class Rk1808(RockchipSoc):
    pid = 0x1808
    sram = RkBinOfficial(LATEST_COMMIT, ddr_933="bin/rk1x/rk1808_ddr_933MHz_v1.06.bin")
    dram = RkBinOfficial(LATEST_COMMIT,
                         usbplug="bin/rk1x/rk1808_usbplug_v1.05.bin",
                         usbplug_noftl="bin/rk1x/rk1808_usbplug_wo_ftl_v1.06.bin")


# RK28 Series
class Rk2818(RockchipSoc):
    pid = 0x281a
    tag = "281X"
    name = "rk2818"


# RK29 Series
class Rk2918(RockchipSoc):
    pid = 0x290a
    name = "rk2918"


class Rk2926_Rk2928(RockchipSoc):
    pid = 0x292a
    rag = "292X"
    name = "rk2926/8"


# RK30 Series
class Rk3026_Rk3028(RockchipSoc):
    pid = 0x292c
    tag = "292X"
    name = "rk3026/8"
    sram = RkBinOfficial(LEGACY_COMMIT,
                         lpddr2_ddr3="30_LPDDR2_300MHz_DDR3_300MHz_20130517.bin",
                         ddr3="RK3036_DDR3_400M_V1.06.bin")
    dram = RkBinOfficial(LEGACY_COMMIT, usbplug="rk30usbplug.bin")


class Rk3032(Rk3026_Rk3028):
    # what is pid?
    pid = None
    name = "rk3032"
    dram = RkBinOfficial(LATEST_COMMIT,
                         usbplug="bin/rk30/rk3032_usbplug_v2.61.bin",
                         usbplug_slc="bin/rk30/rk3032_usbplug_slc_v2.63.bin")


class Rk3036(Rk3026_Rk3028):
    pid = 0x301a
    tag = "301A"
    name = "rk3036"
    dram = RkBinOfficial(LATEST_COMMIT,
                         usbplug="rk303x_usbplug_v2.57.bin",
                         usbplug_slc="rk303x_usbplug_slc_v2.65.bin")


class Rk3066(Rk3026_Rk3028):
    pid = 0x300a
    name = "rk3066"
    tag = "300A"


class Rk3066b(Rk3026_Rk3028):
    pid = 0x310a
    name = "rk3066b"
    tag = "310A"


# RK31 Series
class Rk3126(RockchipSoc):
    pid = 0x310d
    name = "rk3126"
    tag = "310D"
    sram = RkBinOfficial(LATEST_COMMIT, ddr="bin/rk31/rk3126_ddr_300MHz_v2.09.bin")
    dram = RkBinOfficial(LATEST_COMMIT,
                         usbplug="bin/rk31/rk3126_usbplug_v2.63.bin",
                         usbplug_slc="bin/rk31/rk3126_usbplug_slc_v2.63.bin")


class Rk3128(RockchipSoc):
    pid = 0x310c
    name = "rk3128"
    tag = "310C"
    sram = RkBinOfficial(LATEST_COMMIT,
                         ddr="bin/rk31/rk3128_ddr_300MHz_v2.12.bin",
                         ddr_3128x="bin/rk31/rk3128x_ddr_300MHz_v1.08.bin")
    dram = RkBinOfficial(LATEST_COMMIT,
                         usbplug="bin/rk31/rk3128_usbplug_v2.63.bin",
                         usbplug_slc="bin/rk31/rk3128_usbplug_slc_v2.65.bin",
                         usbplug_3128x="bin/rk31/rk3128x_usbplug_v2.57.bin")


class Rk3168(RockchipSoc):
    pid = 0x300b
    name = "rk3168"
    tag = "300B"
    sram = RkBinOfficial(LEGACY_COMMIT, lpddr2_ddr3="3168_LPDDR2_300MHz_DDR3_300MHz_20130517.bin")
    dram = RkBinOfficial(LEGACY_COMMIT, usbplug="rk30usbplug.bin")


class Rk3188(Rk3168):
    pid = 0x310b
    name = "rk3188"
    tag = "310B"
    sram = RkBinOfficial(LATEST_COMMIT, ddr="bin/rk31/bin/rk31/rk3188_ddr_v2.00.bin")
    dram = RkBinOfficial(LATEST_COMMIT, usbplug="bin/rk31/bin/rk31/rk3188_usbplug_v2.00.bin")
