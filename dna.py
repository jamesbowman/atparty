import Image
import math
import numpy as np
import sys
import gameduino.prep as gdprep
import gameduino as gd
import array
import random

def c16(color):
    r = (color >> 10) & 31;
    g = (color >> 5) & 31;
    b = color & 31;
    return (r * 8, g * 8, b * 8)

def swap_rb(c):
    r,g,b = c16(c)
    return gd.RGB(b,g,r) | (c & 0x8000)
def swap_rg(c):
    r,g,b = c16(c)
    return gd.RGB(g,r,b) | (c & 0x8000)
def swap_bg(c):
    r,g,b = c16(c)
    return gd.RGB(r,b,g) | (c & 0x8000)

def loadspr(ir, im, size, ncolors = 16):
    def walktile(im, size):
        for y in range(0, im.size[1], size[1]):
            for x in range(0, im.size[0], size[0]):
                yield im.crop((x, y, x + size[0], y + size[1]))
    tiles = list(walktile(im, size))
    locs = []
    for t in walktile(im, size):
        (page, palsel) = ir.add(array.array('B', t.tostring()), ncolors)
        locs.append((page, gdprep.PALETTE16A[palsel]))
    return locs

cloud = []
NPTS = 125
for i in range(NPTS):
    th = (2 * math.pi * i) / NPTS
    y = -1 + 2 * i / float(NPTS)
    th2 = th * 47
    def pt(th):
        r = 0.7
        r2 = 0.15
        return [127 * (r * math.sin(th) + r2 * math.sin(th2)),
                127 * (r * math.cos(th) + r2 * math.cos(th2)),
                127 * (y)]
    cloud.append(pt(th))
    cloud.append(pt(th + math.pi))

def project(x, y, z):
    distance = 0.0
    xx = x * mat[0] + y * mat[3] + z * mat[6];
    yy = x * mat[1] + y * mat[4] + z * mat[7];
    zz = x * mat[2] + y * mat[5] + z * mat[8] + distance;
    scale = 200;
    q = scale / (250. + zz);
    dx = (511 & int(200 + xx * q)) #  | 
    dy = int(150 + yy * q);
    dz = int(zz * 100);
    cc = (hash(x) & 3)
    return (dx, dy, dz, cc)

mat = [0,0,0, 0,0,0, 0,0,0]

def rotation(phi):
  x = 0.57735026918962573;
  y = 0.57735026918962573;
  z = 0.57735026918962573;

  s = math.sin(phi);
  c = math.cos(phi);

  mat[0] = x*x*(1-c)+c;
  mat[1] = x*y*(1-c)-z*s;
  mat[2] = x*z*(1-c)+y*s;

  mat[3] = y*x*(1-c)+z*s;
  mat[4] = y*y*(1-c)+c;
  mat[5] = y*z*(1-c)-x*s;

  mat[6] = x*z*(1-c)-y*s;
  mat[7] = y*z*(1-c)+x*s;
  mat[8] = z*z*(1-c)+c;

def dna(GD):

    ramp = Image.open("assets/ramp.png")
    (dpic, dchr, dpal) = gdprep.encode(ramp)
    w = ramp.size[0] / 8
    h = ramp.size[1] / 8
    for y in range(h):
        for x in range(0, 50, w):
            GD.m[64 * y + x:64 * y + x + w] = dpic[w*y:w*y+w]
    GD.sync_pic()
    GD.wrstr(gd.RAM_CHR, dchr.tostring())
    GD.wrstr(gd.RAM_PAL, dpal.tostring())

    im = Image.new("RGBA", (64 * 16, 16))
    for i in range(64):
      im.paste(Image.open("assets/lighting%02d.png" % i), (16*i,0))
    im = gdprep.palettize(im, 16)
    im.save("out.png")
    hh = open("../../dna.h", "w")
    ir = gdprep.ImageRAM(hh)
    # ir.addsprites("sphere", (16,16), im, gdprep.PALETTE16A, (8,8))
    locs = loadspr(ir, im, (16, 16))
    print len(ir.used())
    GD.wrstr(gd.RAM_SPRIMG, ir.used())
    sprpal = gdprep.getpal(im)
    GD.wrstr(gd.PALETTE16A, sprpal)
    GD.wrstr(gd.PALETTE16B, array.array('H', [swap_rb(c) for c in sprpal]))
    GD.wrstr(gd.RAM_SPRPAL +    0, array.array('H', [swap_rg(sprpal[i & 15]) for i in range(256)]))
    GD.wrstr(gd.RAM_SPRPAL +  512, array.array('H', [swap_rg(sprpal[i >> 4]) for i in range(256)]))
    GD.wrstr(gd.RAM_SPRPAL + 1024, array.array('H', [swap_bg(sprpal[i & 15]) for i in range(256)]))
    GD.wrstr(gd.RAM_SPRPAL + 1536, array.array('H', [swap_bg(sprpal[i >> 4]) for i in range(256)]))
    """ for i in range(256):
    // palette 0 decodes low nibble, hence (i & 15)
    GD.wr16(RAM_SPRPAL + (i << 1), SWAP_RG(rdpal(i & 15)));
    // palette 1 decodes nigh nibble, hence (i >> 4)
    GD.wr16(RAM_SPRPAL + 512 + (i << 1), SWAP_RG(rdpal(i >> 4)));
   """
    def draw_sphere(slot, x, y, frame, c):
        palix = locs[frame][1] & 1
        pals = {
            0: gdprep.PALETTE16A,
            1: gdprep.PALETTE16B,
            2: (0, 1),
            3: (2, 3)}[c]
        GD.sprite(i, x, y, locs[frame][0], pals[palix])

    GD.hide()

    if 0:
        GD.wrstr(gd.PALETTE16A + 15*2, "aa")
        for i in range(64):
            draw_sphere(i, 64 + 17 * (i & 0xf),
                           116 + 17 * (i / 16), i, 0)
            GD.sync_spr()
            GD.wait()
        GD.wait(60)
        GD.wrstr(gd.PALETTE16A, sprpal)
        GD.wait(60)

        for ii in range(10):
            cols = [random.randrange(4) for i in range(64)]
            for i in range(64):
                draw_sphere(i, 64 + 17 * (i & 0xf),
                               116 + 17 * (i / 16), i, cols[i])
            GD.sync_spr()
            GD.wait(20)

    for f in range(480):
        for i in range(256):
            x = i % 16
            y = i / 16
            wobble = pow(max(0, f - 60) / 420., 1)
            r = 1.5 * wobble * (8 - math.sqrt((x-8)**2 + (y-8)**2))
            dx = math.sin(f * .4) * r
            dy = math.cos(f * .4) * r
            draw_sphere(i,
                        64 + 18 * x + dx,
                         6 + 18 * y + dy,
                        i & 63,
                        i >> 6)
        GD.sync_spr()
        GD.wait()

    GD.hide()
    GD.sync_spr()

    for ii in range(100):
        rotation(ii * 0.02)
        prj = [project(*p) for p in cloud]
        prj = sorted(prj, key=lambda p:-p[2])
        for i,p in enumerate(prj):
            x,y,z,c = p
            frame = max(0, min(63, int(32 + z / 500)))
            draw_sphere(i, x, y, frame, c)
            if ii == 0 and (i & 1):
                GD.sync_spr()
                GD.wait()
        GD.sync_spr()
        GD.wait()
"""
gdprep.dump(hh, "sphere_img", ir.used())
gdprep.dump(hh, "sphere_pal", gdprep.getpal(im))

def r():
    return random.randint(0, 256)

# cloud = [np.array([r(), r(), r()]) for i in range(250)]

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
"""
