#!/usr/bin/python

# Caveman test for receiving simple pings with an RF24 over SPI

import sys
import time
import spidev
from bens_rf24 import bens_rf24
import wiringpi2 as wpi
 
wpi.wiringPiSetup()

radio = bens_rf24(debug=False)

#radio.set_rx_pipeline(chan=0, enable=1, addr=0xE1E1E1E1E1)
#print("\nSet RX pipelines")

radio.set_tx_mode()
print("\nSet TX mode.")

radio.set_tx_pipeline(addr=0xE1E1E1E1E1)
print("\nSet up TX Pipeline")

radio.activate()
print("\nActivated the radio!")

for z in range(0, 5):
  for tx in [ 'Red', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'White', 'off' ]:
    xmitresult = radio.w_tx_payload([ord('L'), ord(tx[0])])
    if xmitresult is False:
      print("Failed after max retries - no acknowledgement")
    else:
      print("Packet sent successfully, {:d} retries required".format(xmitresult))
    
    #print("> CONFIG: 0b{:08b}".format(radio.r_register(0x00, 1)[0]))
    #print("> STATUS: 0b{:08b}".format(radio.getstatus()))
    #print(">   FIFO: 0b{:08b}".format(radio.r_register(0x17, 1)[0]))
    time.sleep(1)

#print("Status: 0b{:08b}".format(radio.getstatus()))
#print("")

print("\nTest completed: {:d} failures".format(radio.r_register(0x08, 1)[0]>>4))

radio.debug_show_pipeconfig()

radio.deactivate()
print("Deactivated the radio")

radio.set_rx_pipeline(chan=0, enable=0)
print("Shut down pipeline 0")

radio.destroy()
print("SPI closed")

