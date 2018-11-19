/****************************************************
  Library for dual side-by-side, 8x8 LED matrix panels.
 ****************************************************/
#include "Arduino.h"

#ifdef __AVR_ATtiny85__
 #include <TinyWireM.h>
#else
 #include <Wire.h>
#endif
#include "Adafruit_GFX.h"

#define LED_RED 1
#define LED_YELLOW 2
#define LED_GREEN 3

class BMA_Dual8x8 {
 public:
  BMA_Dual8x8(void);
  void begin(void);
  void setBrightness(uint8_t b);
  void writeDisplay(void);
  void clear(void);
  void drawPixel(int16_t x, int16_t y, uint16_t color);

  uint16_t redbuffer[8];
  uint16_t greenbuffer[8];

  void init(void);

 private:
  uint8_t i2c_addr[2];
};
