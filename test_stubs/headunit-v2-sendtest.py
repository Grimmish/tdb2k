#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(debug=False)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

for m in range(100):
  for x in range(8):
    for z in range(8):
      if x == z:
        headunit.display.fb['R'][z] = 0xFF
        headunit.display.fb['G'][z] = 0xFF<<8
      else:
        headunit.display.fb['R'][z] = 0
        headunit.display.fb['G'][z] = 0
    headunit.sendBuffer()
    time.sleep(0.1)

radio.destroy()
print("SPI closed")

