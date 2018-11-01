#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit
import wiringpi2 as wpi
 
wpi.wiringPiSetup()

radio = bens_rf24(debug=False)
#radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)
#radio.set_rx_mode()
headunit = rf24_headunit(radio=radio, rxpipe=1, addr=0xE1E1E1E1E1)

#radio.activate()

z = 1.0
flippy = 2.0
colors = [ 'Red', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'White', 'off' ]

while True:
#  for i in range(0, 100):
#    if 
#    time.sleep(0.01)

  print("{:4d}  {:s}".format(int(z), colors[int(z) % (len(colors)-1)]))
  headunit.display(z)
  headunit.led(colors[int(z) % (len(colors)-1)])
  #radio.set_rx_mode()
  z *= flippy
  if (z > -0.5) and (z < 0.5):
    z = z * -1
    flippy = 2
  if (z > 9999) or (z < -999):
    flippy = 0.5

  time.sleep(0.5)

