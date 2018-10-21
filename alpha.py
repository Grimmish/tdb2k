#!/usr/bin/python

# Remember to set PYTHONPATH to find custom modules

import Tkinter as tk
import serial
import time

import gpshelp
from tdb2k_event import tdb2k_event
from tdb2k_data import tdb2k_data
#from tdb2k_gpio import tdb2k_gpio
from tdb2k_display import tdb2k_display

if __name__ == "__main__":
    recorder = tdb2k_data()
    evtmgr = tdb2k_event()
    #gpio = tdb2k_gpio(startPin = 0,
    #                  startAction = evtmgr.doStartEvent,
    #                  stopPin = 1,
    #                  stopAction = evtmgr.doStopEvent)

    root = tk.Tk()
    root.title("TDB2k ALPHA")
    root.attributes("-fullscreen", True)

    window = tdb2k_display(
            master=root,
            startLatch=evtmgr.doStartEvent,
            stopLatch=evtmgr.doStopEvent,
            ghostXfer=recorder.prepGhost
    )

    # Need to bootstrap the evtmgr first so its functions can be hooked
    # into other classes. Once that's set we can actually flesh out
    # the event manager.
    evtmgr.startList.extend(
            [
                recorder.startInstance,
                window.startTime
            ])
    evtmgr.stopList.extend(
            [
                recorder.stopInstance,
                window.stopTime,
                window.refresh_filepicker
            ])
    evtmgr.updateList.extend(
            [
                #gpio.handleEvents,
                window.update_timing,
                window.update_idletasks,
                window.update
            ])


    with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
        ser.reset_input_buffer()
        while True:
            line = ser.readline()
            if line[0:6] != '$GPGGA':
                continue
            (fixtime,lat,lon,quality,sats,alt) = gpshelp.parseGGA(line)
            qual = ("None","GPS","DGPS","PPS","RTK","F-RTK","Est","Man","Sim")[quality]

            if recorder.active:
              recorder.update(gps = {"lat": lat, "lon": lon, "alt": alt})
              if recorder.ghost:
                  window.timer.set("%+03.1f" % recorder.store[-1]["points"][-1]["delta"])
              else:
                  window.timer.set("%03.1f" % recorder.store[-1]["points"][-1]["sessiontime"])

            evtmgr.doUpdateEvent()
