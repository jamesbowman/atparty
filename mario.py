import sys
import math
import Image
import struct
import array
import random

import gameduino as gd
import gameduino.prep as gdprep

def smoothstep(x):
    return 3 * x**2 - 2 * x**3

def mario(GD):
    # GD.getbrush(Image.open("20592.png"))
    # assert 0

    GD.wrstr(gd.RAM_CHR, array.array('H', 256 * ([0xffff] + 7 * [0x300])))
    GD.wrstr(gd.RAM_PAL, array.array('H', 256 * ([0,0,0,gd.RGB(64,64,64)])))
    GD.fill(gd.RAM_PIC, 255, 64 * 38)

    cs = Image.open("assets/20592.png")
    (dpic, dchr, dpal) = gdprep.encode(cs)
    GD.wrstr(gd.RAM_CHR, dchr)
    GD.wrstr(gd.RAM_PAL, dpal)

    if 1:
        for i in range(88):
            x = 10 + (i % 10) * 3
            y = 2 + (i / 10) * 3
            GD.wr(64 * y + x, i)
            GD.wait(2)
        GD.pause()
        GD.fill(gd.RAM_PIC, 255, 64 * 38)
        GD.pause()
    (w,h) = (cs.size[0]/8, cs.size[1]/8)
    def strip(x):
        da = x & 63
        sa = x
        for y in range(h):
            GD.m[da] = dpic[sa]
            sa += w
            da += 64
    for x in range(64):
        strip(x)
        GD.sync_pic()
        # GD.wait(1)
    pix = -1
    scr = 0
    slew = [1] * 72 + [2] * 72
    span = (w - 50) * 8
    part3 = span - 2 * sum(slew)
    vels = slew + ([3] * (part3 / 3)) + slew[::-1]
    r = 0
    for v in vels:
        scr += v
        GD.wait(1)
        GD.scrollxy(scr, 0)
        ix = (scr / 8)
        if (pix != ix) and (ix + 60) < w:
            strip(ix + 60)
            # GD.sync_pic(h)
            pix = ix
        # Sync half of active pic on alternate frames
        bs = 64 * h / 2
        a = r * bs
        GD.wrstr(a, GD.m[a:a+bs])
        r ^= 1
    GD.pause()

    # GD.fill(gd.RAM_CHR + 32 * 16, 0x55, 16) # space
    GD.fill(gd.RAM_CHR + 128 * 16, 0x00, 16) # all-white
    GD.fill(gd.RAM_PIC, 128, 38 * 64)
