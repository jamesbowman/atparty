import sys
import math
import Image
import struct
import array
import random

import gameduino as gd
import gameduino.prep as gdprep

from slide import slide
stretch = [
  0x00, 0x03, 0x0c, 0x0f,
  0x30, 0x33, 0x3c, 0x3f,
  0xc0, 0xc3, 0xcc, 0xcf,
  0xf0, 0xf3, 0xfc, 0xff
]

def setchar(GD, n, bb):
    hh = []
    for b in bb:
        hh.append(stretch[b >> 4])
        hh.append(stretch[b & 15])
    GD.wrstr(gd.RAM_CHR + 16 * n, array.array('B', hh))

def tiling(GD):
    slide(GD, "truchet")
    GD.cold()

    GD.wr16(gd.RAM_PAL + 255*8, gd.RGB(64,64,64))
    GD.fill(gd.RAM_PIC, 255, 4096)

    GD.getbrush(Image.open("assets/truchet.png"))

    for i in range(4):
        GD.wr(64 * 17 + 10 + 10*i, i)
    GD.pause()

    def tr0(x, y):
        return 0
    def tr1(x, y):
        o = (x < 25)
        return (2 * o) + (1 & (x + y))
    def tr2(x, y):
        return [0,2,3,1][(x & 1) | (2*(y & 1))]
    def tr2a(x, y):
        return [1,2,3,0][(x & 1) | (2*(y & 1))]
    def tr3(x, y):
        return [2,3,1,0][(x & 1) | (2*(y & 1))]
    def tr4(x, y):
        return random.randrange(4)
    for f in (tr0, tr1, tr2a, tr2, tr3, tr4):
        b = array.array('B', [f(x, y) for y in range(64) for x in range(64)])
        GD.wrstr(gd.RAM_PIC, b)
        GD.pause()

    GD.cold()
    GD.getbrush(Image.open("assets/diamond03b.gif"))
    GD.paint(5,2)
    GD.sync_pic()
    GD.pause()

    GD.wrstr(gd.RAM_CHR, array.array('H', 256 * ([0xffff] + 7 * [0x300])))

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
    def cls():
        for y in range(25):
            str(0, y, " " * 40)
    cls()

    pal = [gd.RGB(156,156,255),gd.RGB(66,66,222),0,0]
    GD.wrstr(gd.RAM_PAL, array.array('H', 256 * pal))
    GD.wait(10)

    str(4, 1, "**** COMMODORE 64 BASIC V2 ****")
    str(1, 3, "64K RAM SYSTEM  38911 BASIC BYTES FREE")
    str(0, 5, "READY.")
    str(0, 6, "10 PRINT CHR$(205.5+RND(1)); : GOTO 10");
    GD.pause()

    cls()
    GD.wr(20 + 64 * 19, dpic[95])
    GD.wr(30 + 64 * 19, dpic[105])
    GD.pause()

    choice = [random.randrange(2) for i in range(4096)]
    t01 = [xlat[48],xlat[49]]
    tab = [dpic[95],dpic[105]]
    ta1 = [tab[0], t01[1]]
    for t in (t01, ta1, tab):
        print t
        GD.wrstr(0, array.array('B', [t[x] for x in choice]))
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

        GD.wait()
        GD.scrollxy(x, y)
        if i > 200:
            GD.hue(cp, 0.002 * (i-200))
