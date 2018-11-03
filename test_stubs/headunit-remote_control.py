#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit
import wiringpi2 as wpi
 
wpi.wiringPiSetup()

radio = bens_rf24(debug=False)
radio.set_rx_pipeline(chan=1, enable=1, addr=0xE0E0E0E0E0)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

z = 1
colors = [ 'Red', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'White', 'off' ]
headunit.display(z)
headunit.led(colors[z % (len(colors)-1)])

while True:
  if radio.rx_dr():
    evt = (map(chr, radio.r_rx_payload()))
    if int(evt[2]):
      z += (int(evt[1]) * 2) - 3
      headunit.display(z)
      headunit.led(colors[z % (len(colors)-1)])
      print("{:4d}  {:s}".format(z, colors[z % (len(colors)-1)]))
    
  time.sleep(0.001)
