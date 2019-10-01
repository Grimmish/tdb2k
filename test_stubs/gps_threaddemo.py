#!/usr/bin/python

# Remember to set PYTHONPATH to find custom modules

import threading
import serial
import time
import gpshelp

def gps_streamer(gpsdata):
  with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
    ser.reset_input_buffer()
    while True:
        line = ser.readline()
        if line[0:6] != '$GPGGA':
            continue
        (fixtime,lat,lon,quality,sats,alt) = gpshelp.parseGGA(line)
        qual = ("None","GPS","DGPS","PPS","RTK","F-RTK","Est","Man","Sim")[quality]
        gpsdata["GGA"] = { "fixtime": fixtime,
                           "lat": lat,
                           "lon": lon,
                           "quality": qual,
                           "satellites": sats,
                           "altitude": alt }
 
def mainthread():
  gpsdata = { "GGA": None }
  gpsthread = threading.Thread(target=gps_streamer, args=(gpsdata,))
  gpsthread.daemon = True
  gpsthread.start()

  while (True):
    print("Other stuff!")
    if gpsdata["GGA"]:
      print("FIX!: {1:.6f}N/{1:.6f}W".format(gpsdata["GGA"]["lat"], gpsdata["GGA"]["lon"]))
      gpsdata["GGA"] = None

    time.sleep(0.015)


if __name__ == "__main__":
  mainthread()
