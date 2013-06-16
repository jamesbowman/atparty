import array

import Image
import ImageDraw
import ImageFont

import gameduino.prep as gdprep
import gameduino as gd

fonts = {}
for i in range(6, 50):
    fonts[i] = ImageFont.truetype("Vera.ttf", i)

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

def slide(GD, name, *captions):
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

    GD.pause()

    cp = GD.charpal()
    GD.fade(cp, 32, 16)
    for c in captions:
        loadcaption(GD, c)
        drawcaption(GD, (400-256)/2, 180)
        GD.sync_spr()
        GD.pause()
        loadcaption(GD, "")
        GD.wait(18)

    GD.fade(cp, 16, 0)
