import struct
import array
import random

import Image
import ImageDraw
import ImageFont

import gameduino.prep as gdprep
import gameduino as gd

def smoothstep(x):
    return 3 * x**2 - 2 * x**3

def lerp(t, a, b):
    return a + t * (b - a)

def clamp01(x):
    return max(0, min(1, x))

class Sequencer:
    def __init__(self):
        self.f = open("seq", "w")
        self.fake = 0
        self.waitpending = 0

    def sector(self, s):
        self.f.write(s.ljust(512))

    def wrstr(self, addr, s):
        if isinstance(s, array.array):
            s = s.tostring()
        for i in range(0, len(s), 508):
            sub = s[i:i+508]
            print "%04x" % (len(sub) + (self.waitpending << 15)), hex(addr + i)
            self.sector(struct.pack("HH", len(sub) + (self.waitpending << 15), addr + i) + sub)
            self.waitpending = 0
            self.fake += 1
            if self.fake == 8:
                self.fake = 0
                self.wait(1)

    def set0(self, addr, n):
        self.wrstr(addr, chr(0) * n)

    def wait(self, n = 1):
        if n == 1:
            self.waitpending = 1
        else:
            for i in range(n):
                self.sector("." + chr(2))
            self.fake = 0

    def pause(self):
        if 0:
            self.sector("," + chr(2))
        else:
            self.wait(60)

from phony import Gameduino

s = Sequencer()
GD = Gameduino(s)

from playback import playback
from scroll import scroll
from tiling import tiling
from dna import dna
from blocks import blocks
from mario import mario

def do(nm):
    if 0 or nm in ('scroll'):
        print 'doing', nm
        return True
    else:
        return False

def loadspr(ir, im, size, ncolors = 16):
    def walktile(im, size):
        for y in range(0, im.size[1], size[1]):
            for x in range(0, im.size[0], size[0]):
                yield im.crop((x, y, x + size[0], y + size[1]))
    tiles = list(walktile(im, size))
    locs = []
    for t in walktile(im, size):
        (page, palsel) = ir.add(array.array('B', t.tostring()), ncolors)
        locs.append((page, palsel))
    return locs

fonts = {}
for i in range(10, 50):
    fonts[i] = ImageFont.truetype("Vera.ttf", i)

def loadcaption(GD, msg, color = (255,255,255)):
    # caption area is 256x32
    # Sprite slots 128 up, and pages 56-63 available
    # 32 4-color pages
    im = Image.new("RGBA", (256, 32))
    dr = ImageDraw.Draw(im)
    for sz in sorted(fonts, reverse = True):
        font = fonts[sz]
        (w,h) = font.getsize(msg)
        if (w <= 256) and (h <= 32):
            break
    # assert 0, str(sz)
    x = (256 - w) / 2
    y = (32 - h) / 2
    for xd in range(-3,4):
        for yd in range(-2,3):
            dr.text((x+xd,y+yd), msg, font=font, fill=(0,0,0))
    dr.text((x,y), msg, font=font, fill=color)

    im = gdprep.palettize(im, 4)
    ir = gdprep.ImageRAM(None)
    loadspr(ir, im, (16,16), 4)
    GD.wrstr(gd.RAM_SPRIMG + 1024 * 14, ir.used())
    sprpal = gdprep.getpal(im)
    GD.wrstr(gd.PALETTE4A, sprpal)

def drawcaption(GD, x, y):
    for i in range(32):
        GD.sprite(128 + i, x + 16 * (i % 16), y + 16 * (i / 16), 56 + (i/4), 8 + (i & 3) * 2)

def static(name, *captions):
    f = open("originals/%s.img" % name)
    pic = f.read(4096)
    cha = f.read(4096)
    sprimg = f.read(16384)
    spr = f.read(1024)
    pal = f.read(2048)
    pal16a = f.read(32)

    # s.set0(gd.RAM_PIC, 64 * 38)
    # s.set0(gd.RAM_SPR, 1024)
    GD.wrstr(gd.RAM_PAL, pal)
    GD.wrstr(gd.PALETTE16A, pal16a)
    GD.wrstr(gd.RAM_CHR, cha)
    GD.wrstr(gd.RAM_SPRIMG, sprimg[:1024 * 14])
    GD.wrstr(gd.RAM_SPR, spr)
    GD.wrstr(gd.RAM_PIC, pic[:64 * 38])

    s.pause()

    cp = GD.charpal()
    GD.fade(cp, 32, 16)
    for c in captions:
        loadcaption(GD, c)
        drawcaption(GD, (400-256)/2, 180)
        GD.sync_spr()
        s.pause()
        loadcaption(GD, "")
        s.wait(18)

    GD.fade(cp, 16, 0)

if do('statics'):
    GD.cold()
    static("atparty")
    static("eagle")
    static("pitch")
    static("Kickstarter0")
    static("odyssey")
    static("ball")
    static("frogger")
    static("zardoz")
    static("wargames", "layers, sprites, palettes", "32K ROM, 2K RAM", "beam chasing")
    static("backto", "C++", "big storage", "desktop tools")

if do('mario'):
    GD.cold()
    mario(GD)

if do('scroll'):
    GD.cold()
    scroll(GD)

if do('tiling'):
    GD.cold()
    tiling(GD)

if do('dna'):
    GD.cold()
    dna(GD)

if do('blocks'):
    GD.cold()
    blocks(GD)

if do('demos'):
    for d in ['ball','chessboard','asteroids', 'manicminer']:
        GD.cold()
        playback(GD, open("traces/" + d))

GD.cold()
GD.getbrush(Image.open("originals/atparty.png"))
GD.paint(0,0)
cp = GD.charpal()
GD.fadechars(cp, 0)
GD.sync_pic()
GD.fade(cp, 0, 32)
