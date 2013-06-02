import struct
import array

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

from phony import Gameduino

s = Sequencer()
GD = Gameduino(s)

from scroll import scroll
from dna import dna

# scroll(GD)
# dna(GD)

order = [(gd.RAM_PIC,4096), (gd.RAM_CHR,4096), (gd.RAM_SPRIMG,16384), (gd.RAM_SPR, 1024), (gd.RAM_PAL,2048), (gd.PALETTE16A, 32)]

for name in ("atparty", "backto", "wargames"):
    continue
    f = open("originals/%s.img" % name)
    pic = f.read(4096)
    cha = f.read(4096)
    sprimg = f.read(16384)
    spr = f.read(1024)
    pal = f.read(2048)
    pal16a = f.read(32)

    s.set0(gd.RAM_PIC, 64 * 36)
    s.set0(gd.RAM_SPR, 1024)
    s.wrstr(gd.RAM_PAL, pal)
    s.wrstr(gd.PALETTE16A, pal16a)
    s.wrstr(gd.RAM_CHR, cha)
    s.wrstr(gd.RAM_SPRIMG, sprimg)
    s.wrstr(gd.RAM_SPR, spr)
    s.wrstr(gd.RAM_PIC, pic[:64 * 36])

    s.wait(60)

writes = (-1, [])

def wflush():
    if writes[1]:
        print 'flush %x' % writes[0], len(writes[1])
        GD.wrstr(writes[0], array.array('B', writes[1]))

