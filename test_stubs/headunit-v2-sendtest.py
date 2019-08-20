#!/usr/bin/python

import sys
import time
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit

radio = bens_rf24(debug=False)
headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)

headunit.radio.set_tx_pipeline(headunit.addr)
headunit.radio.w_tx_payload([ord('D'), ord('R'), 0b00001000, 0b00000000,
                                                 0b00010100, 0b00000000,
                                                 0b00100010, 0b00000000,
                                                 0b01000001, 0b00000001,
                                                 0b10000000, 0b10000010,
                                                 0b00000000, 0b01000100,
                                                 0b00000000, 0b00101000,
                                                 0b10100101, 0b00010000 ])

headunit.radio.w_tx_payload([ord('D'), ord('G'), 0b00010000, 0b00000000,
                                                 0b00101000, 0b00000000,
                                                 0b01000100, 0b00000001,
                                                 0b10000010, 0b00000010,
                                                 0b00000001, 0b00000100,
                                                 0b00000000, 0b10001000,
                                                 0b00000000, 0b01010000,
                                                 0b10100101, 0b00100000 ])

radio.destroy()
print("SPI closed")

