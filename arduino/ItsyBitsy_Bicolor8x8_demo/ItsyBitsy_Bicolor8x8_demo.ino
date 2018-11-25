/*************************************************** 
  This is a library for our I2C LED Backpacks

  Designed specifically to work with the Adafruit LED Matrix backpacks 
  ----> http://www.adafruit.com/products/872
  ----> http://www.adafruit.com/products/871
  ----> http://www.adafruit.com/products/870

  These displays use I2C to communicate, 2 pins are required to 
  interface. There are multiple selectable I2C addresses. For backpacks
  with 2 Address Select pins: 0x70, 0x71, 0x72 or 0x73. For backpacks
  with 3 Address Select pins: 0x70 thru 0x77

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Wire.h>
//#include "Adafruit_LEDBackpack.h"
//#include "Adafruit_GFX.h"
#include "BMA_Dual8x8.h"

#define DELAYCONST 30

BMA_Dual8x8 scr = BMA_Dual8x8();
void setup() {
  scr.begin();
}

int bounce_x = 0;
int bounce_y = 2;
int direction_x = 1;
int direction_y = 1;
int bounce_c = LED_GREEN;

void loop() {

  for (int ch=120; ch<123; ch++) {
    for (int z=16; z>7; z--) {
      scr.clear();
      scr.drawMiniChar(z, 2, ch, LED_GREEN);
      scr.writeDisplay();
      delay(DELAYCONST);
    }
    delay(DELAYCONST * 8);
    for (int z=7; z>-4; z--) {
      scr.clear();
      scr.drawMiniChar(z, 2, ch, LED_RED);
      scr.writeDisplay();
      delay(DELAYCONST);
    }
  }

  scr.clear();
  scr.writeDisplay();

  for (int z=0; z<120; z++) {
    if ((bounce_x == 0) || (bounce_x == scr._width-1) || (bounce_y == 0) || (bounce_y == scr._height-1)) {
      bounce_c = LED_RED;
    } else {
      bounce_c = LED_GREEN;
    }

    scr.clear();
    scr.drawPixel(bounce_x, bounce_y, bounce_c);
    scr.writeDisplay();
    delay(DELAYCONST);

    bounce_x += direction_x;
    bounce_y += direction_y;

    if ((bounce_x < 0) || (bounce_x >= scr._width)) {
      direction_x *= -1;
      bounce_x += direction_x * 2;
    }
    if ((bounce_y < 0) || (bounce_y >= scr._height)) {
      direction_y *= -1;
      bounce_y += direction_y * 2;
    }
  }

  scr.clear();
  scr.writeDisplay();

  for (int y=0; y<8; y += 2) {
    for (int x=15; x>=0; x--) {
      scr.greenbuffer[y] |= 1<<x;
      scr.writeDisplay();
      delay(DELAYCONST);
    }
    scr.clear();
    scr.writeDisplay();
    for (int x=15; x>=0; x--) {
      scr.redbuffer[y+1] |= 1<<x;
      scr.writeDisplay();
      delay(DELAYCONST);
    }
    scr.clear();
    scr.writeDisplay();
  }

  /*
  for (int z=0; z<8; z++) {
    for (int i=0; i<8; i++) {
      scr.greenbuffer[i] = 0x00FF;
      scr.redbuffer[i] = 0x00FF;
    }
    scr.writeDisplay();
    delay(35);

    for (int i=0; i<8; i++) {
      scr.greenbuffer[i] = 0;
      scr.redbuffer[i] = 0;
    }
    scr.writeDisplay();
    delay(35);

    for (int i=0; i<8; i++) {
      scr.greenbuffer[i] = 0xFF00;
      scr.redbuffer[i] = 0xFF00;
    }
    scr.writeDisplay();
    delay(35);

    for (int i=0; i<8; i++) {
      scr.greenbuffer[i] = 0;
      scr.redbuffer[i] = 0;
    }
    scr.writeDisplay();
    delay(35);
  }
  */
}
