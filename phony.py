import struct
import array
import gameduino as gd
import gameduino.prep as gdprep
import colorsys

def c16(color):
    r = (color >> 10) & 31;
    g = (color >> 5) & 31;
    b = color & 31;
    return (r * 8, g * 8, b * 8)

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

    def pause(self):
        self.t.pause()

    def sprite(self, spr, x, y, image, palette = 0, rot = 0, jk = 0):
        x = int(x)
        y = int(y)
        assert spr < 512
        p = gd.RAM_SPR + spr * 4
        self.m[p + 0] = x & 0xff
        self.m[p + 1] = (palette << 4) | (rot << 1) | ((x >> 8) & 1);
        self.m[p + 2] = y & 0xff;
        self.m[p + 3] = (jk << 7) | (image << 1) | ((y >> 8) & 1);

    def hide(self):
        for i in range(512):
            self.sprite(i, 400, 400, 0)

    def cold(self):
        self.wr(gd.J1_RESET, 1);              # HALT coprocessor
        self.wr(gd.SPR_DISABLE, 1);
        self.fill(gd.RAM_PAL, 0, 1024 * 2);  # Zero all character RAM
        self.fill(gd.PALETTE16A, 0, 128);     # Black 16-, 4-palletes and COMM
        self.fill(gd.RAM_PIC, 0, 1024 * 8);  # Zero all character RAM
        self.fill(gd.RAM_SPRPAL, 0, 2048);    # Sprite palletes black
        self.fill(gd.RAM_SPR, 0, 64 * 256);   # Clear all sprite data
        self.fill(gd.VOICES, 0, 256);         # Silence

        self.hide()
        self.sync_spr()

        self.wr16(gd.SCROLL_X, 0);
        self.wr16(gd.SCROLL_Y, 0);
        self.wr(gd.JK_MODE, 0);
        self.wr(gd.SPR_DISABLE, 0);
        self.wr(gd.SPR_PAGE, 0);
        self.wr(gd.IOMODE, 0);
        self.wr16(gd.BG_COLOR, 0);
        self.wr16(gd.SAMPLE_L, 0);
        self.wr16(gd.SAMPLE_R, 0);
        self.wr16(gd.SCREENSHOT_Y, 0);

    def get_spr(self):
        return self.m[gd.RAM_SPR:gd.RAM_SPR + 1024]

    def sync_spr(self):
        self.t.wrstr(gd.RAM_SPR, self.get_spr())

    def sync_pic(self):
        self.t.wrstr(gd.RAM_PIC, self.m[gd.RAM_PIC:gd.RAM_PIC+4096])

    def fill(self, a, v, count):
        self.wrstr(a, chr(v) * count)

    def wr(self, a, v):
        self.wrstr(a, struct.pack("B", int(v) & 0xff))
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

    def charpal(self):
        # Return the current char palette
        return array.array('H', (
            self.m[gd.RAM_PAL:gd.RAM_PAL+2048].tostring() +
            self.m[gd.PALETTE16A:gd.PALETTE16A+32].tostring()))

    def fadechars(self, ch, t):
        rgb = [c16(h) for h in ch]
        def fc(v):
            return max(0, min(255, int(v * t)))
        rgb = [(fc(r), fc(g), fc(b)) for (r,g,b) in rgb]
        newpal = array.array('H', [gd.RGB(*c) for c in rgb]).tostring()
        self.wrstr(gd.RAM_PAL, newpal[0:2048])
        self.wrstr(gd.PALETTE16A, newpal[2048:2048+32])

    def fade(self, ch, a, b):
        for i in range(a, b, cmp(b, a)):
            self.fadechars(ch, i / 31.)
            self.wait()
        self.fadechars(ch, b / 31.)

    def hue(self, ch, t):
        rgb = [c16(h) for h in ch]
        def f(r, g, b):
            (h,s,v) = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
            h += t
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
            return tuple([max(0, min(255, int(c * 255))) for c in (r, g, b)])

        rgb = [f(r,g,b) for (r,g,b) in rgb]
        newpal = array.array('H', [gd.RGB(*c) for c in rgb]).tostring()
        self.wrstr(gd.RAM_PAL, newpal[0:2048])
        self.wrstr(gd.PALETTE16A, newpal[2048:2048+32])
