#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(debug=True)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

as_bytes = [ord('D'), ord('R')] + [ 0b00001000, 0b00000000,
                                    0b00010100, 0b00000000,
                                    0b00100010, 0b00000000,
                                    0b01000001, 0b00000001,
                                    0b10000000, 0b10000010,
                                    0b00000000, 0b01000100,
                                    0b00000000, 0b00101000,
                                    0b00000000, 0b00010000 ]
headunit.radio.set_tx_pipeline(headunit.addr)
headunit.radio.w_tx_payload(as_bytes)

radio.destroy()
print("SPI closed")

