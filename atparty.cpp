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

#ifdef EMULATED
static FILE *ff;

static void sdcard_begin()
{
  ff = fopen("seq", "r");
}

static byte readsector(byte *sec)
{
  return fread(sec, 512, 1, ff) != 0;
}
#else

#define SDCARD_CS 8       // Which pin is sdcard enable connected to?
#include "sdcard.h"

static Reader rr;

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
  rr.openfile("MAIN.SEQ");
}

static byte readsector(byte *sec)
{
  byte ok = (rr.offset < rr.size);
  if (ok)
    rr.readsector(sec);
  return ok;
}

#endif

void setup()
{
  GD.begin();
  controller_init();
  sdcard_begin();

  byte sec[512];
  while (readsector(sec)) {
    uint16_t count = sec[0] + (sec[1] << 8);
    uint16_t addr = sec[2] + (sec[3] << 8);
    if (count < 0x200) {
      byte *pc = sec + 4;
      GD.__wstart(addr);
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
        while (controller_sense(0) == CONTROL_RIGHT)
          ;
        while (controller_sense(0) != CONTROL_RIGHT)
          if (controller_sense(0) == CONTROL_DOWN)
            exit(0);
      }
    }
    if (controller_sense(0) == CONTROL_DOWN)
      exit(0);
  }

}

void loop()
{
  if (controller_sense(0))
    exit(0);
}
