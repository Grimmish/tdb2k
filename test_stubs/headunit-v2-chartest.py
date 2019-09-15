#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(debug=False)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

headunit.display.drawChar('8', 0, 0, 'R')
headunit.display.drawChar('8', 13, 3, 'G')
headunit.sendBuffer()
time.sleep(1)

for z in range(-3, 6):
  headunit.display.floodColor('B')
  headunit.display.drawChar('8', z, (z-2), 'Y')
  headunit.sendBuffer()
  time.sleep(0.05)

time.sleep(0.5)
for z in range(17, 7, -1):
  headunit.display.floodColor('B')
  headunit.display.drawChar('8', z, (z-8), 'Y')
  headunit.sendBuffer()
  time.sleep(0.05)

time.sleep(1)
headunit.display.floodColor('R')
headunit.display.drawString('yeet', 0, 1, 'B')
for m in range(10):
  headunit.display.setBrightness(15)
  headunit.sendBuffer()
  time.sleep(0.05)
  headunit.display.setBrightness(3)
  headunit.sendBuffer()
  time.sleep(0.05)


radio.destroy()
print("SPI closed")

