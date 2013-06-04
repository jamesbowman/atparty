import array

import gameduino as gd

class Combiner:
    def __init__(self, GD):
        self.GD = GD
        self.m = GD.m
        self.areas = [None for i in range(32768)]
        for (a, n) in [
            (gd.IDENT, 32), # registers
            (gd.VOICES, 256),
            (gd.PALETTE16A, 32 + 32 + 8 + 8),
            (gd.COMM, 16),
            (gd.J1_CODE, 256),
            (gd.RAM_PIC,4096),
            (gd.RAM_CHR,4096),
            (gd.RAM_PAL,2048),
            (gd.RAM_SPRIMG,16384),
            (gd.RAM_SPR, 2048),
            (gd.RAM_SPRPAL, 2048),
            (gd.PALETTE16A, 32)]:
            for i in range(a, a + n):
                self.areas[i] = a
        self.writing = False
        self.merging = False
    def flush(self):
        if self.writing:
            # print 'write %04x - %04x' % (self.lo, self.hi)
            self.GD.wrstr(self.lo, self.m[self.lo:self.hi + 1])
            self.writing = False
    def wr(self, a, v):
        if self.merging is not None:
            if self.merging == self.areas[a]:
                pass # continue merging
            else:
                # New area. Flush.
                self.flush()
        else:
            self.flush()
        self.merging = self.areas[a]
        if not self.writing:
            self.lo = a
            self.hi = a
            self.writing = True
        else:
            self.lo = min(self.lo, a)
            self.hi = max(self.hi, a)
        self.m[a] = v

def playback(GD, tracefile):
    cc = Combiner(GD)
    for l in tracefile:
        if l.startswith("__"):
            fl = l[2:].split()
            if fl[0] == 'START':
                a = int(fl[1], 16) & 0x7fff
            elif fl[0] == 'WRITE':
                cc.wr(a, int(fl[1], 16))
                a += 1
            elif fl[0] == 'END':
                pass
            elif fl[0] == 'WAIT':
                cc.flush()
                # print 'WAIT'
                GD.wait()
            else:
                assert 0, "Unknown command %r" % fl
