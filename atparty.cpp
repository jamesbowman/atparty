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

static FILE *ff;
#define NEXT1() getc(ff)
uint16_t NEXT2()
{
  byte lo = NEXT1();
  byte hi = NEXT1();
  return lo + (hi << 8);
}

static void loadto(uint16_t addr, uint16_t count)
{
  GD.__wstart(addr);
  for (int i = 0; i < count; i++)
    SPI.transfer(getc(ff));
  GD.__end();
}

// readsector: read sector, returns 0 if at EOF
#ifdef EMULATED
static byte readsector(byte *sec)
{
  return fread(sec, 512, 1, ff) != 0;
}
#endif

void setup()
{
  GD.begin();
  controller_init();

  ff = fopen("seq", "r");
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
