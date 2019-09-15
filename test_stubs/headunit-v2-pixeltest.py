#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(debug=False)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

headunit.display.floodColor('B')
headunit.sendBuffer()
for z in range(3):
  headunit.display.drawPixel(0, z, 'R')
  headunit.display.drawPixel(z, 0, 'R')
  headunit.display.drawPixel(0, (7-z), 'Y')
  headunit.display.drawPixel(z, 7, 'Y')
  headunit.display.drawPixel(15, z, 'Y')
  headunit.display.drawPixel((15-z), 0, 'Y')
  headunit.display.drawPixel(15, (7-z), 'G')
  headunit.display.drawPixel((15-z), 7, 'G')
  headunit.sendBuffer()
  time.sleep(0.3)

for z in range(4):
  headunit.display.drawPixel(z, 3, 'R')
  headunit.display.drawPixel(3, z, 'R')
  headunit.display.drawPixel(z, 4, 'Y')
  headunit.display.drawPixel(3, (7-z), 'Y')
  headunit.display.drawPixel((15-z), 3, 'Y')
  headunit.display.drawPixel(12, z, 'Y')
  headunit.display.drawPixel((15-z), 4, 'G')
  headunit.display.drawPixel(12, (7-z), 'G')
  headunit.sendBuffer()
  time.sleep(0.3)

for z in range(4,8):
  headunit.display.drawPixel(z, 3, 'R')
  headunit.display.drawPixel(z, 4, 'Y')
  headunit.display.drawPixel((15-z), 3, 'Y')
  headunit.display.drawPixel((15-z), 4, 'G')
  headunit.sendBuffer()
  time.sleep(0.3)


radio.destroy()
print("SPI closed")

