#include <SPI.h>
#include <GD.h>

// ----------------------------------------------------------------------
//     controller: buttons on Arduino pins 3,4,5,6 with 7 grounded
// ----------------------------------------------------------------------

static void controller_init()
{
  // Configure input pins with internal pullups
  byte i;
  for (i = 3; i < 7; i++) {
    pinMode(i, INPUT);
    digitalWrite(i, HIGH);
  }
  // drive pin 7 low
  pinMode(7, OUTPUT);
  digitalWrite(7, 0);
}

#define CONTROL_LEFT  1
#define CONTROL_RIGHT 2
#define CONTROL_UP    4
#define CONTROL_DOWN  8

static byte controller_sense(uint16_t clock)
{
  byte r = 0;

  if (!digitalRead(5))
    r |= CONTROL_DOWN;
  if (!digitalRead(4))
    r |= CONTROL_UP;
  if (!digitalRead(6))
    r |= CONTROL_LEFT;
  if (!digitalRead(3))
    r |= CONTROL_RIGHT;
  return r;
}

// sdcard_begin: init sdcard
// readsector: read sector, returns 0 if at EOF

#if !defined(EMULATED)

#define SDCARD_CS 8       // Which pin is sdcard enable connected to?
#include "sdcard.h"

static void sdcard_begin()
{
  pinMode(SDCARD_CS, OUTPUT);
  digitalWrite(SDCARD_CS, HIGH);
  delay(100);
  SD.begin(SDCARD_CS);
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPSR = (1 << SPI2X);
}
#else
static void sdcard_begin() {}

class Reader {
public:
  FILE *f;
  void openfile(const char *name) {
    f = fopen(name, "r");
    if (!f) {
      perror(name);
      exit(1);
    }
  }
  int eof(void) {
    return feof(f);
  }
  int readsector(byte *dst) {
    fread(dst, 512, 1, f);
    return !feof(f);
  }
  void skipsector() {
    byte buf[512];
    fread(buf, 512, 1, f);
  };
};
#endif

int atxy(int x, int y)
{
  return (y << 6) + x;
}

void show_stripes()
{
  int y = 5;
  int i;

  for (i = 0; i < 32; i++) {
    GD.wr16(RAM_PAL + (0x80 + i) * 8, RGB(8 * i, 0, 0));
    GD.wr16(RAM_PAL + (0xa0 + i) * 8, RGB(0, 8 * i, 0));
    GD.wr16(RAM_PAL + (0xc0 + i) * 8, RGB(0, 0, 8 * i));
    GD.wr(atxy(i + 9, y + 24), 0x80 + i);
    GD.wr(atxy(i + 9, y + 25), 0xa0 + i);
    GD.wr(atxy(i + 9, y + 26), 0xc0 + i);
  }
}

static byte button()
{
  return !digitalRead(3);
}

static void wait_button()
{
  while (button())
    delay(10);
  while (!button())
    delay(10);
}

static void banner()
{
  digitalWrite(3, HIGH);
  delay(50);
  byte mode = button() ? MODE_800x600_60  : MODE_800x600_72;

  GD.wr(VIDEO_MODE, mode);
  GD.ascii();
  show_stripes();
  GD.putstr(15, 12, "READY.  PRESS START");
  GD.putstr(23, 17, (mode == MODE_800x600_72) ? "72 HZ" : "60 HZ");
  byte ch = '@';
  byte b, pb;
  b = pb = button();

  while (!(pb==0 && b==1)) {
    for (byte i = 8; i; i--)
      GD.waitvblank();
    GD.fill(atxy(0, 0), ch, 50);
    GD.fill(atxy(0, 36), ch, 50);
    for (byte i = 1; i < 36; i++) {
      GD.wr(atxy(0, i), ch);
      GD.wr(atxy(49, i), ch);
    }
    if (++ch > 'Z')
      ch = '@';
    pb = b;
    b = button();
  }
}



void setup()
{
  // Serial.begin(115200);
  GD.begin();
  controller_init();
  banner();
  sdcard_begin();

#if 0
  rickroll();

  for (int i = 0; i < 256; i++) {
    GD.wr16(RAM_PAL + (4 * i + 0) * 2, RGB(0,0,0));
    GD.wr16(RAM_PAL + (4 * i + 1) * 2, RGB(0x20,0x20,0x20));
    GD.wr16(RAM_PAL + (4 * i + 2) * 2, RGB(0x40,0x40,0x40));
    GD.wr16(RAM_PAL + (4 * i + 3) * 2, RGB(0xff,0xff,0xff));
  }
  GD.microcode(random_code, sizeof(random_code));
  for (;;)
    ;
#endif

  for (;;) {
    Reader seq;
    seq.openfile("MAIN.SEQ");
    byte sec[512];
    while (!seq.eof()) {
      seq.readsector(sec);
      uint16_t count = sec[0] + (sec[1] << 8);
      uint16_t addr = sec[2] + (sec[3] << 8);
      if (count & 0x8000) {
        GD.waitvblank();
        count &= 0x7fff;
      }
      if (count < 0x200) {
        byte *pc = sec + 4;
        GD.__wstart(addr);
        while (count > 8) {
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          SPI.transfer(*pc++);
          count -= 8;
        }
        while (count--)
          SPI.transfer(*pc++);
        GD.__end();
      } else {
        switch (count & 0xff) {
        case '.':
          GD.waitvblank();
          break;
        case ',':
          delay(1);
#ifdef EMULATED
         while (controller_sense(0) == CONTROL_RIGHT)
           ;
         while (controller_sense(0) != CONTROL_RIGHT)
            if (controller_sense(0) == CONTROL_DOWN)
              exit(0);
#else
          wait_button();
#endif
        }
      }
      if (controller_sense(0) == CONTROL_DOWN)
        exit(0);
    }
  }
}

void loop()
{
  if (controller_sense(0))
    exit(0);
}
