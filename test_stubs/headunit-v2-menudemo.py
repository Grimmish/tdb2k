#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit,BicolorMatrix16x8

def changePixmap(menuitem, args):
  if menuitem['label'] == 'checkmark':
    menuitem['label'] = 'target'
  else:
    menuitem['label'] = 'checkmark'
  menuitem['labeltype'] = 'pixart'
  return menuitem

def changeToSecs(menuitem, args):
  menuitem['label'] = time.strftime('%S', time.localtime())
  menuitem['labeltype'] = 'string'
  return menuitem

radio = bens_rf24(addr=0xE0E0E0E0E0, debug=False)
radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)

headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)
headunit.radio.set_rx_mode()

headunit.menu.tree[1]['dofunction'] = changePixmap
headunit.menu.tree[1]['do_args'] = []

headunit.menu.tree[0]['submenu'][1]['showfunction'] = changeToSecs
headunit.menu.tree[0]['submenu'][1]['show_args'] = []

headunit.drawCurrentMenuItem()

deadswitch = time.time()

print("Waiting forever... (use CTRL+C to break out)")
while True:
  time.sleep(0.01)

  #if (time.time() - deadswitch > 2.3):
  #  print "DEAD SWITCH! No contact in 2.3 seconds. REBOOT THE RADIO!"
  #  radio = bens_rf24(addr=0xE0E0E0E0E0, debug=False)
  #  radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)
  #  headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)
  #  headunit.radio.set_rx_mode()
  #  headunit.menu.tree[1]['dofunction'] = changePixmap
  #  headunit.menu.tree[1]['do_args'] = []
  #  headunit.drawCurrentMenuItem()
  #  deadswitch = time.time()

  if headunit.radio.rx_dr():
    deadswitch = time.time()
    packet = "".join(map(chr, headunit.radio.r_rx_payload()))
    print("Message!: " + packet)
    if packet.startswith('P1'):
      # Ping request, headunit is lonely. Resend the display buffer.
      headunit.sendBuffer()
    elif packet[0] == 'B' and packet[2] == '1':
      if packet[1] == '1':
        # Red button
        headunit.menuAction('up')
      elif packet[1] == '2':
        # Green button
        headunit.menuAction('down')
      elif packet[1] == '3':
        # Yellow button
        headunit.menuAction('select')
      else:
        continue


radio.destroy()
print("SPI closed")
