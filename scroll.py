import sys
import math
import Image
import struct
import array

import gameduino as gd
import gameduino.prep as gdprep

def scroll(GD):
    # assets/4311669609_cdb83b6286_o.jpg
    # assets/4299180244_cd6099a2fd_o.jpg
    tile = Image.open("assets/4293136099_3bb98722c0_o.jpg").resize((128,128),Image.BILINEAR)
    GD.wrstr(gd.RAM_CHR, array.array('H', 256 * ([0xffff] + 7 * [0x300])))
    GD.wrstr(gd.RAM_PAL, array.array('H', 256 * ([0,0,0,gd.RGB(255,255,255)])))
    (dpic, dchr, dpal) = gdprep.encode(tile)
    # self.wrstr(gd.RAM_CHR, dchr.tostring())
    # self.wrstr(gd.RAM_PAL, dpal.tostring())
    pic = [(16 * (y & 15) + (x & 15)) for y in range(64) for x in range(64)]
    GD.wrstr(gd.RAM_PIC, array.array('B', pic))
    for i in range(256):
        a = gd.RAM_PAL + 8 * i
        GD.wr16(a, gd.RGB(255, 0, 0))
        GD.wait()
        GD.wr16(a, gd.RGB(0, 0, 0))
    for i in range(256):
        GD.wrstr(gd.RAM_CHR + 16 * i, dchr[16 * i:16 * i + 16])
        GD.wrstr(gd.RAM_PAL + 8 * i, dpal[4 * i:4 * i + 4])
        GD.wait()
    return

    GD.getbrush(tile)
    for x in range(0, 64, 16):
        for y in range(0, 64, 16):
            GD.paint(x, y)
            GD.sync_pic()
            if 0:
                if x == 0 and y == 0:
                    GD.wait(60)
                else:
                    GD.wait(8)
    print 
    coords = [(i, 0) for i in range(256)]
    coords += [(0, i) for i in range(256)]

    phi = 0
    for f in range(480*2):
        t = min(f / 480., 1)
        pt = math.pow(t, 2)
        phi += pt * 0.01
        r = 1024 + 1024 * t
        coords.append((r * math.sin(phi), r * math.cos(phi)))

    for (x, y) in coords:
        GD.wrstr(gd.SCROLL_X, struct.pack("HH", int(x) & 511, int(y) & 511))
        GD.wait()
    cp = GD.charpal()
    GD.fade(cp, 32, 0)

