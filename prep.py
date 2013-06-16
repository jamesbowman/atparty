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
        self.f = open("MAIN.SEQ", "w")
        self.fake = 0
        self.waitpending = 0

    def sector(self, s):
        self.f.write(s.ljust(512))

    def wrstr(self, addr, s):
        if isinstance(s, array.array):
            s = s.tostring()
        for i in range(0, len(s), 508):
            sub = s[i:i+508]
            # print "%04x" % (len(sub) + (self.waitpending << 15)), hex(addr + i)
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
        self.sector("," + chr(2))

if 0:
    cs = Image.open("assets/sonic.png")
    (dpic, dchr, dpal) = gdprep.encode(cs)
    print 'sonic used', len(dchr) / 16
    sys.exit(0)

from phony import Gameduino

s = Sequencer()
GD = Gameduino(s)

from slide import slide
from playback import playback
from scroll import scroll
from tiling import tiling
from dna import dna
from blocks import blocks
from mario import mario
from j1 import j1

def do(nm):
    if 1 or nm in ('tiling', ):
        print 'doing', nm
        return True
    else:
        return False

if do('statics'):
    GD.cold()
    slide(GD, "atparty")
    slide(GD, "eagle")
    slide(GD, "pitch")
    slide(GD, "Kickstarter0")
    slide(GD, "DSC_2222-500")
    slide(GD, "blog-gameduino1")
    slide(GD, "odyssey")
    slide(GD, "ball")
    slide(GD, "frogger")
    slide(GD, "zardoz")
    slide(GD, "wargames", "layers, sprites, palettes", "32K ROM, 2K RAM", "beam chasing")
    slide(GD, "backto", "Wiring / C++", "big storage", "desktop tools")
    slide(GD, "plato", "algorithms", "math", "taste")

if do('mario'):
    GD.cold()
    mario(GD)

if do('scroll'):
    GD.cold()
    scroll(GD)

if do('tiling'):
    GD.cold()
    tiling(GD)

if do('blocks'):
    GD.cold()
    blocks(GD)

if do('dna'):
    GD.cold()
    dna(GD)

if do('j1'):
    GD.cold()
    j1(GD)

if do('demos'):
    for d in ['ball', 'chessboard', 'asteroids', 'manicminer']:
        GD.cold()
        playback(GD, open("traces/" + d))
        GD.pause()

GD.cold()
GD.getbrush(Image.open("originals/atparty.png"))
GD.paint(0,0)
cp = GD.charpal()
GD.fadechars(cp, 0)
GD.sync_pic()
GD.fade(cp, 0, 32)
