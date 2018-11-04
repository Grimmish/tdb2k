#!/usr/bin/python

# Caveman test for receiving simple pings with an RF24 over SPI

import sys
import time
import spidev
from bens_rf24 import bens_rf24

radio = bens_rf24(debug=False)
radio.set_tx_pipeline(addr=0xE1E1E1E1E1)
radio.set_tx_mode()

for z in range(0, 5):
  for tx in [ 'Red', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'White', 'off' ]:
    xmitresult = radio.w_tx_payload([ord('L'), ord(tx[0])])
    if xmitresult > 0:
      print("Packet sent successfully, {:d} attempts required".format(xmitresult))
    else:
      print("Failed after max retries - no acknowledgement")
    
    time.sleep(1)

print("\nTest completed: {:d} failures".format(radio.r_register(0x08, 1)[0]>>4))

radio.destroy()
print("SPI closed")

