#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit,BicolorMatrix16x8

radio = bens_rf24(addr=0xE0E0E0E0E0, debug=False)
radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)

headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)
headunit.radio.set_rx_mode()

menulist = [ 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz' ]
menuindex = 0
submenumode = False
nextitem = BicolorMatrix16x8()
slidedirection = ''

# Background & nav elements
headunit.display.floodColor('B')
headunit.display.drawPixart('pointerup', 13, 0, 'R')
headunit.display.drawPixart('2x2square', 14, 3, 'Y')
headunit.display.drawPixart('pointerdown', 13, 6, 'G')

# Initial selection
headunit.display.drawString(menulist[menuindex], 1, 1, 'Y')
headunit.sendBuffer()

print("Waiting forever... (use CTRL+C to break out)")
while True:
  if headunit.radio.rx_dr():
    packet = "".join(map(chr, headunit.radio.r_rx_payload()))
    print("Button!: " + packet)
    if packet[0] == 'B' and packet[2] == '1':
      nextitem.floodColor('B')
      if packet[1] == '1' and not submenumode:
        # Red button: up
        menuindex -= 1
        if menuindex < 0: menuindex = len(menulist) - 1
        nextitem.drawString(menulist[menuindex], 1, 1, 'Y')
        slidedirection = 'down'
      elif packet[1] == '2' and not submenumode:
        # Green button: down
        menuindex += 1
        if menuindex == len(menulist): menuindex = 0
        nextitem.drawString(menulist[menuindex], 1, 1, 'Y')
        slidedirection = 'up'
      elif packet[1] == '3':
        # Yellow button: select
        if submenumode:
          # Drop back to main menu
          nextitem.drawString(menulist[menuindex], 1, 1, 'Y')
          slidedirection = 'right'
        else:
          nextitem.drawPixart('checkmark', 1, 1, 'G')
          slidedirection = 'left'
        submenumode = not submenumode
      else:
        continue

      headunit.slideTransition(slidedirection, nextitem, 0.02)

radio.destroy()
print("SPI closed")
