import Image
import math
import numpy as np
import sys
import gameduino.prep as gdprep
import gameduino.remote
import gameduino
import array
import random

im = Image.new("RGBA", (64 * 16, 16))
for i in range(64):
  im.paste(Image.open("lighting%02d.png" % i), (16*i,0))
im = gdprep.palettize(im, 16)
im.save("out.png")
hh = open("../../dna.h", "w")
ir = gdprep.ImageRAM(hh)
ir.addsprites("sphere", (16,16), im, gdprep.PALETTE16A, (8,8))
print len(ir.used())
gdprep.dump(hh, "sphere_img", ir.used())
gdprep.dump(hh, "sphere_pal", gdprep.getpal(im))

def r():
    return random.randint(0, 256)

# cloud = [np.array([r(), r(), r()]) for i in range(250)]
cloud = []
for i in range(125):
    th = (2 * math.pi * i) / 125
    y = -1 + 2 * i / 125.
    th2 = th * 47
    def pt(th):
        r = 0.7
        r2 = 0.15
        return [r * math.sin(th) + r2 * math.sin(th2),
                r * math.cos(th) + r2 * math.cos(th2), y]
    cloud.append(pt(th))
    cloud.append(pt(th + math.pi))

print >>hh, "static PROGMEM prog_char cloud[] = {"
for i,p in enumerate(cloud):
    x,y,z = p
    print >>hh, "%d,%d,%d," % tuple(127 * c for c in p)
print >>hh, "};"

ramp = Image.open("ramp.png").convert("L")
q32 = [min(0xf8, (c + random.randrange(8)) & ~7) for c in array.array('B', ramp.tostring())]
ramp = Image.fromstring("L", ramp.size, array.array('B', q32))
for i in range(0, len(q32), (32 * 8)):
    print i, set(q32[i : i + 24*8])

fn = "ramp"
(picdata, chrdata, paldata) = gdprep.encode(ramp.convert("RGB"))
gdprep.dump(hh, "%s_pic" % fn, array.array('B', [b + 128 for b in picdata]))
gdprep.dump(hh, "%s_chr" % fn, chrdata)
gdprep.dump(hh, "%s_pal" % fn, paldata)
monoh = []
for h in paldata:
    r = 31 & (h >> 10)
    g = 31 & (h >> 5)
    b = 31 & (h >> 0)
    if len(set([r,g,b])) != 1:
        print "%04x" % h, r, g, b
    monoh.append((r << 10) | (r << 5) | r)


if 0:
    def r():
        return -1 + 2 * random.random()

    cloud = [np.array([r(), r(), r()]) for i in range(250)]

    gd = gameduino.remote.Gameduino("/dev/ttyUSB0", 115200)
    gd.wrstr(gameduino.PALETTE16A, gdprep.getpal(im))
    gd.wr16(gameduino.RAM_PAL, gameduino.RGB(10, 30, 70))
    gd.wrstr(gameduino.RAM_SPRIMG, ir.used())

    print cloud
    i = 0
    scloud = [p for (_,p) in sorted([(-z,(x,y,z)) for (x,y,z) in cloud])]
    for i,p in enumerate(scloud):
        x,y,z = p
        z = int(32 + 31 * z)
        sprimg = z / 2
        sprpal = [4,6][z%2]
        gd.sprite(i, int(200 + 200 * x), int(150 + 200 * y), sprimg, sprpal, 0)
