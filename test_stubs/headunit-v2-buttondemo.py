#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(addr=0xE0E0E0E0E0, debug=False)
radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)

headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)
headunit.radio.set_rx_mode() # Not really necessary; RX mode is default

print("Waiting forever... (use CTRL+C to break out)")

while True:
  if headunit.radio.rx_dr():
    print("Packet!")
    packet = "".join(map(chr, headunit.radio.r_rx_payload()))
    print(">> Payload: " + packet)
    if packet[0] == 'B':
      if packet[2] == '0':
        # Release
        headunit.display.floodColor('B')

      else:
        if packet[1] == '1':
          headunit.display.floodColor('R')
        if packet[1] == '2':
          headunit.display.floodColor('G')
        if packet[1] == '3':
          headunit.display.floodColor('Y')

      headunit.sendBuffer()

radio.destroy()
print("SPI closed")
