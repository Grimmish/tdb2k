#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(debug=False)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

z = 1
colors = [ 'Red', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'White', 'off' ]

while z < 10000:
  print("{:4d}  {:s}".format(z, colors[z % (len(colors)-1)]))
  headunit.display(z)
  headunit.led(colors[z % (len(colors)-1)])
  time.sleep(0.5)
  z *= 3

z /= 3

while z > 0:
  print("{:4d}  {:s}".format(z, colors[z % (len(colors)-1)]))
  headunit.display(z)
  headunit.led(colors[z % (len(colors)-1)])
  time.sleep(0.5)
  z /= 2

radio.destroy()
print("SPI closed")

