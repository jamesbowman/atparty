import struct
import array
import random

import Image

import gameduino.prep as gdprep
import gameduino as gd

class Sequencer:
    def __init__(self):
        self.f = open("seq", "w")
        self.fake = 0

    def sector(self, s):
        self.f.write(s.ljust(512))

    def wrstr(self, addr, s):
        if isinstance(s, array.array):
            s = s.tostring()
        for i in range(0, len(s), 508):
            sub = s[i:i+508]
            self.sector(struct.pack("HH", len(sub), addr + i) + sub)
            self.fake += 1
            if self.fake == 8:
                self.fake = 0
                self.wait(1)

    def set0(self, addr, n):
        self.wrstr(addr, chr(0) * n)

    def wait(self, n = 1):
        for i in range(n):
            self.sector("." + chr(2))
        self.fake = 0

    def pause(self):
        self.sector("," + chr(2))

from phony import Gameduino

s = Sequencer()
GD = Gameduino(s)

from playback import playback
from scroll import scroll
from tiling import tiling
from dna import dna

GD.cold()
for name in (
#    "atparty",
#    "eagle", "pitch", "Kickstarter0",
#    "odyssey", "ball", "frogger", "zardoz",
#    "wargames",
#    "backto",
    ):
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

    # Sprite slots 128 up, and pages 56-63 available
    # 32 4-color pages
    GD.wrstr(gd.PALETTE4A, array.array('H', [gd.RGB(0,0,0), gd.RGB(85,85,85), gd.RGB(170, 170, 170), gd.RGB(255,255,255)]))
    GD.wrstr(gd.RAM_SPRIMG + 1024 * 14, array.array('B', [random.randrange(256) for i in range(2048)]))
    for i in range(32):
        GD.sprite(128 + i, 17 * (i % 16), 100 + 17 * (i / 16), 56 + (i/4), 8 + (i & 3) * 2)
    GD.sync_spr()

    s.wait(120)

    cp = GD.charpal()
    GD.fade(cp, 32, 0)

if 1:
    GD.cold()
    tiling(GD)

if 0:
    GD.cold()
    scroll(GD)

if 0:
    GD.cold()
    dna(GD)

if 0:
    GD.cold()
    playback(GD, open("traces/chessboard"))
    GD.cold()
    playback(GD, open("traces/ball"))
    GD.cold()
    playback(GD, open("traces/asteroids"))
