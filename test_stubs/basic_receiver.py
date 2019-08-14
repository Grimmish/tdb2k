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

radio.set_rx_mode() # Not really necessary; RX mode is default
radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)
print("\nActivated the radio!!!\n")
radio.debug_show_pipeconfig()

print("\nListening for 30 seconds:\n")
for i in range(0, 300):
  if (radio.rx_dr()):
    print(" [ {:d} ] Payload: |{:s}|".format(i, "".join(map(chr, radio.r_rx_payload()))))
  #else:
  #  print(" [ {:d} ] (No data)".format(i))
  time.sleep(0.1)

radio.set_rx_pipeline(chan=0, enable=0)
print("Shut down pipeline 0")

radio.destroy()
print("SPI closed")
