/****************************************************
  Library for dual side-by-side, 8x8 LED matrix panels.
 ****************************************************/

#ifdef __AVR_ATtiny85__
 #include <TinyWireM.h>
 #define Wire TinyWireM
#else
 #include <Wire.h>
#endif
#include "BMA_Dual8x8.h"
#include "Adafruit_GFX.h"

#ifndef _BV
  #define _BV(bit) (1<<(bit))
#endif

BMA_Dual8x8::BMA_Dual8x8(void)
{
  for (int i=0; i<8; i++) {
    redbuffer[i] = 0;
    greenbuffer[i] = 0;
  }
}

void BMA_Dual8x8::setBrightness(uint8_t b) {
  if (b > 15) b = 15;
  Wire.beginTransmission(i2c_addr[0]);
  Wire.write(0xE0 | b);
  Wire.endTransmission();
  Wire.beginTransmission(i2c_addr[1]);
  Wire.write(0xE0 | b);
  Wire.endTransmission();
}

void BMA_Dual8x8::begin(void) {
  i2c_addr[0] = 0x70;
  i2c_addr[1] = 0x71;
  Wire.begin();
  Wire.beginTransmission(i2c_addr[0]);
  Wire.write(0x21);
  Wire.endTransmission();
  Wire.beginTransmission(i2c_addr[1]);
  Wire.write(0x21);
  Wire.endTransmission();
  setBrightness(15);
}

void BMA_Dual8x8::writeDisplay(void) {
  /*
    Each element of redbuffer[] and greenbuffer[] describe a horizontal
    row as a 16-bit word. E.g., (greenbuffer[0] = 1<<15) would put a
    dot in the upper left.
    
    However, the registers on the hardware controller must be written
    out in vertical columns using 8-bit words; first the green word,
    then the red. The hardware register automatically advances
    to accept the next pair of words.
  */

  // First the right-side display
  Wire.beginTransmission(i2c_addr[1]);
  Wire.write((uint8_t)0x00); // Reset to position 0/0
  for (uint8_t x=0; x<8; x++) {
    uint8_t greenbyte = 0;
    uint8_t redbyte = 0;
    for (uint8_t y=0; y<8; y++) {
      greenbyte |= ((greenbuffer[y] >> x) & 1) << y;
      redbyte |= ((redbuffer[y] >> x) & 1) << y;
    }
    Wire.write(greenbyte);
    Wire.write(redbyte);
  }
  Wire.endTransmission();

  // Then the left
  Wire.beginTransmission(i2c_addr[0]);
  Wire.write((uint8_t)0x00); // Reset to position 0/0
  for (uint8_t x=8; x<16; x++) {
    uint8_t greenbyte = 0;
    uint8_t redbyte = 0;
    for (uint8_t y=0; y<8; y++) {
      greenbyte |= ((greenbuffer[y] >> x) & 1) << y;
      redbyte |= ((redbuffer[y] >> x) & 1) << y;
    }
    Wire.write(greenbyte);
    Wire.write(redbyte);
  }
  Wire.endTransmission();

}
