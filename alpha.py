#!/usr/bin/python

# Remember to set PYTHONPATH to find custom modules

import Tkinter as tk
import serial
import time
import threading
import Queue

import gpshelp
from tdb2k_event import tdb2k_event
from tdb2k_data import tdb2k_data
#from tdb2k_gpio import tdb2k_gpio
from tdb2k_display import tdb2k_display
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit,BicolorMatrix16x8

state = "menu" # Primary reference for current mode: menu, ready, run, postrun
stateset = time.time()

def gps_handler(gpsdata):
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


def radio_handler(radioqueue, radio):
  while True:
    while radioqueue['out'].qsize() > 0:
      outmsg = radioqueue['out'].get()
      # FIXME: Will we ever actually send raw packets out from this thread?
    if radio.rx_dr():
      radioqueue['in'].put("".join(map(chr, radio.r_rx_payload())))


def menuaction(menuitem, args):
  action = args[0]
  headunit = args[1]
  if action == "makeready":
    state = "ready"
    stateset = time.time()
    headunit.display.floodColor('B')
    headunit.display.drawString('RDY!', 0, 1, 'Y')
    headunit.sendBuffer()
  return menuitem

def mainthread():
  recorder = tdb2k_data()
  evtmgr = tdb2k_event()
  #gpio = tdb2k_gpio(startPin = 0,
  #                  startAction = evtmgr.doStartEvent,
  #                  stopPin = 1,
  #                  stopAction = evtmgr.doStopEvent)
  radio = bens_rf24(addr=0xE0E0E0E0E0, debug=False)
  radio.set_rx_pipeline(chan=0, enable=1, addr=0xE0E0E0E0E0)
  headunit = rf24_headunit(radio=radio, addr=0xE1E1E1E1E1)
  headunit.radio.set_rx_mode()

  # Enrich some menu functions
  headunit.menu.tree[0]['dofunction'] = menuaction
  headunit.menu.tree[0]['do_args'] = [ 'makeready', headunit ]

  root = tk.Tk()
  root.title("TDB2k ALPHA")
  root.attributes("-fullscreen", True)

  window = tdb2k_display(
          master=root,
          startLatch=evtmgr.doStartEvent,
          stopLatch=evtmgr.doStopEvent,
          ghostXfer=recorder.prepGhost
  )

  gpsdata = { "GGA": None }
  gpsthread = threading.Thread(target=gps_handler, args=(gpsdata,))
  gpsthread.daemon = True
  gpsthread.start()

  radioqueue = { "in": Queue.Queue(),
                 "out": Queue.Queue() }
  radiothread = threading.Thread(target=radio_handler, args=(radioqueue,radio,))
  radiothread.daemon = True
  radiothread.start()

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


  while True:

    if radioqueue['in'].qsize() > 0:
      inmsg = radioqueue['in'].get()
      if inmsg.startswith("P0"):
        headunit.sendBuffer()

      if state == "menu" and inmsg[0] == "B" and inmsg[2] == '1':
        if inmsg[1] == '1': # Red button
          headunit.menuAction('up')
        elif inmsg[1] == '2': # Green button
          headunit.menuAction('down')
        elif inmsg[1] == '3': # Yellow button
          headunit.menuAction('select')

      # Cancel ready mode
      if state == "ready" and inmsg == "B11":
        state = "menu"
        stateset = time.time()
        headunit.drawCurrentMenuItem()

      # GO!
      if state == "ready" and (inmsg == "I21" or inmsg == "B21"):
        evtmgr.doStartEvent();
        state = "run"
        stateset = time.time()

      # STOP!
      if state == "run" and (inmsg == "I31" or inmsg.startswith("B")):
        evtmgr.doStopEvent();
        state = "postrun"
        stateset = time.time()

    if state == "postrun" and time.time() - stateset > 10:
      state = "menu"
      stateset = time.time()
      headunit.drawCurrentMenuItem()

    if gpsdata["GGA"] and recorder.active:
      recorder.update(gps = {"lat": lat, "lon": lon, "alt": alt})
      if recorder.ghost:
        delta = recorder.store[-1]["points"][-1]["delta"]
        window.timer.set('{+5.1f}'.format(delta))
        if delta > 0.1:
          c = 'R'
        elif delta >= -0.1:
          c = 'Y'
        else:
          c = 'G'
        headunit.display.floodColor('B')
        headunit.display.drawString('{:4.1f}'.format(elapsed), 0, 1, c)
        headunit.sendBuffer()
      else:
        elapsed = recorder.store[-1]["points"][-1]["sessiontime"]
        window.timer.set('{:5.1f}'.format(elapsed))
        headunit.display.floodColor('B')
        headunit.display.drawString('{:4.1f}'.format(elapsed), 0, 1, 'Y')
        headunit.sendBuffer()
      gpsdata['GGA'] = None


    #FIXME Do we even need this any more? Where does it go?
    evtmgr.doUpdateEvent()

    time.sleep(0.01)   # I guess?


if __name__ == "__main__":
  mainthread()
