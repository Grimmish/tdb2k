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

#include "minifont.c"
#include <avr/pgmspace.h>

#ifndef _BV
  #define _BV(bit) (1<<(bit))
#endif

BMA_Dual8x8::BMA_Dual8x8(void) {
  for (int i=0; i<8; i++) {
    redbuffer[i] = 0;
    greenbuffer[i] = 0;
  }
  _width  = WIDTH;
  _height = HEIGHT;
}

void BMA_Dual8x8::setBrightness(uint8_t b) {
  if (b > 15) b = 15;
  for (int i=0; i<2; i++) {
    Wire.beginTransmission(i2c_addr[i]);
    Wire.write(0xE0 | b);
    Wire.endTransmission();
  }
}

void BMA_Dual8x8::begin(void) {
  i2c_addr[0] = 0x70;
  i2c_addr[1] = 0x71;
  for (int i=0; i<2; i++) {
    Wire.begin();
    Wire.setClock(400000); // Superfast!
    Wire.beginTransmission(i2c_addr[i]);
    Wire.write(0x21); // Activate the onboard oscillator
    Wire.endTransmission();
    Wire.beginTransmission(i2c_addr[i]);
    Wire.write(0xE0 | 15); // Set the brightness (0-15)
    Wire.endTransmission();
    Wire.beginTransmission(i2c_addr[i]);
    Wire.write(0x81); // Turn on the display (no blink)
    Wire.endTransmission();
  }
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

void BMA_Dual8x8::clear(void) {
  for (int i=0; i<8; i++) {
    redbuffer[i] = 0;
    greenbuffer[i] = 0;
  }
}

void BMA_Dual8x8::drawPixel(int16_t x, int16_t y, uint16_t color) {
  // 0,0 is top-left; (_width-1),(height-1) is bottom-right

  // ignore out-of-bounds coordinates
  if ((x < 0) ||
      (x >= _width) ||
      (y < 0) ||
      (y >= _height))
    return;

  if (color == LED_RED) {
    redbuffer[y] |= 1<<(_width-1-x);      // ON
    greenbuffer[y] &= ~(1<<(_width-1-x)); // off
  }
  else if (color == LED_GREEN) {
    redbuffer[y] &= ~(1<<(_width-1-x));   // off
    greenbuffer[y] |= 1<<(_width-1-x);    // ON
  }
  else if (color == LED_YELLOW) {
    redbuffer[y] |= 1<<(_width-1-x);      // ON
    greenbuffer[y] |= 1<<(_width-1-x);    // ON
  }
  else {
    redbuffer[y] &= ~(1<<(_width-1-x));   // off
    greenbuffer[y] &= ~(1<<(_width-1-x)); // off
  }
}

void BMA_Dual8x8::drawMiniChar(int16_t x, int16_t y, unsigned char c, uint16_t color) {
  /* Chars are stored as 16-bit words that represent the
     3x5 bitmap as five 3-bit stripes:
        012
        345
        678
        9AB
        CDE
     (The highest bit is unused)  */
  uint16_t word = pgm_read_word(minifont+c);
  for (int8_t stripe=0; stripe<5; stripe++) {
    for (int8_t col=0; col<3; col++) {
      uint8_t pixel;
      if (word>>((stripe*3)+col) & 1) {
        pixel = color;
      } else {
        pixel = LED_OFF;
      }
      drawPixel(x+col, y+stripe, pixel);
    }
  }
}

void BMA_Dual8x8::printError(void) {
  for (int i=1; i<16; i+=4) {
    drawMiniChar(i, 1, 1, LED_RED);
  }
}

void BMA_Dual8x8::printDec(double n, uint16_t color) {
  uint8_t numericDigits = 3; // Max we can accommodate
  boolean isNegative = false;

  if (n < 0) {
    isNegative = true;
    --numericDigits;
    n *= -1;
  }

  // Shift the decimal to the right so we can ignore the rest
  uint32_t displayNumber = n * 10 + 0.5;

  // What's the largest number we can display given current constraints?
  uint32_t tooBig = 1;
  for(int i = 0; i < numericDigits; ++i) tooBig *= 10;

  clear();
  if (displayNumber >= tooBig) {
    printError();
  } else {
    // Render digits right-to-left; always render 2 right-most digits
    char thisdigit = '0' + (displayNumber % 10);
    drawMiniChar(12, 1, thisdigit, color);

    drawPixel(10, 5, color);

    thisdigit = '0' + ((displayNumber/10) % 10);
    drawMiniChar(6, 1, thisdigit, color);

    if (isNegative) {
      drawMiniChar(2, 1, 0x2D, color);
    }
    else if (displayNumber > 100) {
      thisdigit = '0' + ((displayNumber/100) % 10);
      drawMiniChar(2, 1, thisdigit, color);
    }
  }
}








