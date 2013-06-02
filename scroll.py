import math
import Image
import struct

import gameduino as gd
import gameduino.prep as gdprep

def scroll(GD):
    tile = Image.open("assets/4293136099_3bb98722c0_o.jpg").resize((128,128),Image.BILINEAR)
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

