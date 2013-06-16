import sys
import math
import Image
import struct
import array
import random

import gameduino as gd
import gameduino.prep as gdprep
import slide

random_code = array.array('B', [
0x81,0x15,
0x00,0x80,
0xED,0xFF,
0x00,0x66,
0x00,0x60,
0x00,0x6C,
0x81,0x61,
0x23,0x60,
0x03,0x61,
0x00,0x6A,
0xFF,0x9F,
0x03,0x63,
0x82,0x15,
0x0C,0x70,
])

def j1(GD):
    GD.wrstr(gd.RAM_PAL, array.array('H', 256 * ([
        gd.RGB(0,0,0),
        gd.RGB(0x20,0x20,0x20),
        gd.RGB(0x40,0x40,0x40),
        gd.RGB(0xff,0xff,0xff)
    ])))
    GD.microcode(random_code);
    GD.wr(gd.SPR_DISABLE, 0);
    s = "".join(["%02X" % c for c in random_code])
    for c in ('16-bit, 50 MIPS', '256 bytes code', 'full access', 'random', s):
        slide.loadcaption(GD, c)
        slide.drawcaption(GD, (400-256)/2, 180)
        GD.sync_spr()
        GD.pause()
        slide.loadcaption(GD, "")
        GD.wait(18)
