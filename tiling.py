import sys
import math
import Image
import struct
import array
import random

import gameduino as gd
import gameduino.prep as gdprep

def tiling(GD):
    # GD.getbrush(Image.open("20592.png"))
    # assert 0

    cs = Image.open("assets/c64_low.gif").crop((0,0,256,32))
    (dpic, dchr, dpal) = gdprep.encode(cs)
    GD.wrstr(gd.RAM_CHR, dchr)
    GD.fill(gd.RAM_CHR + 32 * 16, 0x55, 16) # space
    GD.fill(gd.RAM_CHR + 128 * 16, 0x00, 16) # all-white
    GD.fill(gd.RAM_PIC, 128, 38 * 64)

    xlat = [0 for i in range(128)]
    for i in range(32):
        xlat[0x60 + i] = i
        xlat[0x20 + i] = 32 + i
        xlat[0x40 + i] = 64 + i
    def str(x, y, s):
        GD.wrstr((7+y) * 64 + (5+x), array.array('B', [xlat[ord(c)] for c in s]))
    for y in range(25):
        str(0, y, " " * 40)

    pal = [gd.RGB(156,156,255),gd.RGB(66,66,222),0,0]
    GD.wrstr(gd.RAM_PAL, array.array('H', 256 * pal))
    GD.wait(10)

    str(4, 1, "**** COMMODORE 64 BASIC V2 ****")
    str(1, 3, "64K RAM SYSTEM  38911 BASIC BYTES FREE")
    str(0, 5, "READY.")
    str(0, 6, "10 PRINT CHR$(205.5+RND(1)); : GOTO 10");
    GD.pause()
    s = array.array('B', [random.choice((dpic[95], dpic[105])) for i in range(4096)])
    GD.wrstr(0, s)
    GD.pause()
    cp = GD.charpal()
    GD.fade(cp, 32, 0)

    GD.wrstr(gd.RAM_CHR, array.array('H', 256 * ([0xffff] + 7 * [0x300])))
    GD.wrstr(gd.RAM_PAL, array.array('H', 256 * ([0,0,0,gd.RGB(64,64,64)])))
    GD.fill(gd.RAM_PIC, 255, 64 * 38)

    tile = Image.open("assets/4312221289_3ae3d8e306_o.jpg").resize((128,128),Image.BILINEAR)
    (dpic, dchr, dpal) = gdprep.encode(tile)
    GD.wrstr(gd.RAM_CHR, dchr)
    GD.wrstr(gd.RAM_PAL, dpal)
    
    def paint(x0, y0, i):
        sx = 4 * i
        for y in range(4):
            GD.wrstr(64 * (y0+y) + x0, dpic[sx:sx+4])
            sx += 16
    for i in range(4):
        paint(14 + 6 * i, 17, i)
    GD.pause()

    for x in range(0, 64, 4):
        for y in range(0, 64, 4):
            if ((x ^ y) & 4) == 0:
                ti = random.choice((0,2))
            else:
                ti = random.choice((1,3))
            paint(x, y, ti)

    cp = GD.charpal()

    x = 0
    for i in range(960):
        y = 3 * i
        x = 50 * math.sin(i * 0.01)

        if i > 200:
            GD.hue(cp, 0.002 * (i-200))

        GD.wrstr(gd.SCROLL_X, struct.pack("HH", int(x) & 511, int(y) & 511))
        GD.wait()
