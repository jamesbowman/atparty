import struct
import array
import gameduino as gd
import gameduino.prep as gdprep

class Gameduino:
    def __init__(self, t):
        self.m = array.array('B', chr(0) * 32768)
        self.t = t

    def wrstr(self, a, s):
        if isinstance(s, array.array):
            s = s.tostring()
        self.m[a:a+len(s)] = array.array('B', s)
        self.t.wrstr(a, s)

    def wait(self, *args):
        self.t.wait(*args)

    def sprite(self, spr, x, y, image, palette = 0, rot = 0, jk = 0):
        x = int(x)
        y = int(y)
        assert spr < 256
        p = gd.RAM_SPR + spr * 4
        self.m[p + 0] = x & 0xff
        self.m[p + 1] = (palette << 4) | (rot << 1) | ((x >> 8) & 1);
        self.m[p + 2] = y & 0xff;
        self.m[p + 3] = (jk << 7) | (image << 1) | ((y >> 8) & 1);

    def hide(self):
        for i in range(256):
            self.sprite(i, 400, 400, 0)

    def get_spr(self):
        return self.m[gd.RAM_SPR:gd.RAM_SPR + 1024]

    def sync_spr(self):
        self.t.wrstr(gd.RAM_SPR, self.get_spr())

    def sync_pic(self):
        self.t.wrstr(gd.RAM_PIC, self.m[gd.RAM_PIC:gd.RAM_PIC+4096])

    def wr16(self, a, v):
        self.wrstr(a, struct.pack("H", int(v) & 0xffff))

    def getbrush(self, im):
        (dpic, dchr, dpal) = gdprep.encode(im)
        self.wrstr(gd.RAM_CHR, dchr.tostring())
        self.wrstr(gd.RAM_PAL, dpal.tostring())
        self.dpic = dpic
        self.w = im.size[0] / 8
        self.h = im.size[1] / 8

    def paint(self, x, y0):
        w = self.w
        h = self.h
        for y in range(h):
            self.m[64 * (y0+y) + x:64 * (y0+y) + x + self.w] = self.dpic[w*y:w*y+w]
