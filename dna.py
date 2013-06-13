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

def norm(x, y, z):
    d = math.sqrt(x**2 + y**2 + z**2)
    return (x / d, y / d, z / d)

def rotation(phi, x, y, z):
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

class Ball:
    def __init__(self):
        self.x = random.random() * 400
        self.y = random.random() * 300
        th = random.random() * 2 * math.pi
        r = 3
        self.dx = r * math.sin(th)
        self.dy = r * math.cos(th)
    def move(self):
        self.x += self.dx
        if self.x < 0:
            self.x = -self.x
            self.dx *= -1
        if self.x > 400:
            self.x = 800-self.x
            self.dx *= -1
        self.y += self.dy
        if self.y < 0:
            self.y = -self.y
            self.dy *= -1
        if self.y > 284:
            self.y = (2 * 284)-self.y
            self.dy *= -1
    def fall(self):
        self.dy += .3
        v = math.sqrt(self.dx ** 2 + self.dy ** 2)
        self.dx *= 0.999
        self.dy *= 0.999
        self.move()

def dna(GD):

    if 0:
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
    else:
        GD.getbrush(Image.open("originals/atparty.png"))
        GD.paint(0,0)
        GD.sync_pic()
    cp = GD.charpal()
    GD.fade(cp, 32, 8)

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

    if 1:
        GD.wrstr(gd.PALETTE16A + 15*2, "aa")
        for i in range(64):
            draw_sphere(i, 64 + 17 * (i & 0xf),
                           116 + 17 * (i / 16), i, 0)
            GD.sync_spr()
            GD.wait()
        GD.pause()
        GD.wrstr(gd.PALETTE16A, sprpal)
        GD.pause()

        for ii in range(10):
            cols = [random.randrange(4) for i in range(64)]
            for i in range(64):
                draw_sphere(i, 64 + 17 * (i & 0xf),
                               116 + 17 * (i / 16), i, cols[i])
            GD.sync_spr()
            GD.wait(20)
        GD.pause()

    for i in range(256):
        x = i % 16
        y = i / 16
        draw_sphere(i,
                    64 + 18 * x,
                     6 + 18 * y,
                    i & 63,
                    i >> 6)
    GD.sync_spr()
    GD.pause()

    mcloud = [Ball() for i in range(256)]
    for ii in range(480):
        for i,b in enumerate(mcloud):
            draw_sphere(i, b.x, b.y, i & 63, i >> 6)
        if ii < 320:
            [b.move() for b in mcloud]
        else:
            [b.fall() for b in mcloud]
        GD.sync_spr()
        GD.wait(1)

    GD.hide()
    GD.sync_spr()
    GD.pause()

    phi = 1.0
    for ii in range(60 * 20):
        rotation(phi, *norm(math.sin(ii / 77.), 1, 1))
        phi += 0.027
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
    GD.pause()
