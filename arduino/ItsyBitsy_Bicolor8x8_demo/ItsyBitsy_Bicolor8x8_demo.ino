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

#define DELAYCONST 15

BMA_Dual8x8 scr = BMA_Dual8x8();
void setup() {
  scr.begin();
}

void loop() {
  for (int y=0; y<8; y += 2) {
    for (int x=15; x>=0; x--) {
      scr.greenbuffer[y] |= 1<<x;
      scr.writeDisplay();
      delay(DELAYCONST);
    }
    for (int x=15; x>=0; x--) {
      scr.redbuffer[y+1] |= 1<<x;
      scr.writeDisplay();
      delay(DELAYCONST);
    }
  }

  for (int x=15; x>0; x-=2) {
    for (int y=0; y<8; y++) {
      scr.greenbuffer[y] |= 1<<x;
      scr.writeDisplay();
      delay(DELAYCONST);
    }
    for (int y=0; y<8; y++) {
      scr.redbuffer[y] |= 1<<(x-1);
      scr.writeDisplay();
      delay(DELAYCONST);
    }
  }

  for (int i=0; i<8; i++) {
    scr.greenbuffer[i] = 0;
    scr.redbuffer[i] = 0;
  }
  scr.writeDisplay();
}
