#!/usr/bin/env python

# Caveman test for receiving simple pings with an RF24 over SPI

import time
import spidev
import bens_rf24
import wiringpi2 as wpi
import sys
 
wpi.wiringPiSetup()

radio = bens_rf24.bens_rf24(debug=False)
print("\nFinished initializing. RX pipeline status:")
radio.debug_show_pipeconfig()

radio.activate()
radio.set_rx_mode()
radio.set_rx_pipeline(chan=0, enable=1, addr=1)
print("\nActivated the radio!!!\n")
radio.debug_show_pipeconfig()

for i in range(0, 20):
  if (radio.rx_dr()):
    print(" [ {:d} ] Payload: |{:s}|".format(i, "".join(map(chr, radio.r_rx_payload()))))
  else:
    print(" [ {:d} ] (No data)".format(i))
  time.sleep(0.5)

radio.deactivate()
print("Deactivated the radio")

radio.set_rx_pipeline(chan=0, enable=0)
print("Shut down pipeline 0")

radio.destroy()
print("SPI closed")