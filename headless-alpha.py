#!/usr/bin/python

# Remember to set PYTHONPATH to find custom modules

#import Tkinter as tk
import serial
import time
import threading
import Queue
import os
import json

import gpshelp
from tdb2k_event import tdb2k_event
from tdb2k_data import tdb2k_data
#from tdb2k_gpio import tdb2k_gpio
from bens_rf24 import bens_rf24
from rf24_headunit import rf24_headunit,BicolorMatrix16x8

state = "menu" # Primary reference for current mode: menu, ready, run, postrun
stateset = time.time()
diffmode = 'OFF'
pickfile = None

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
                         "qual": qual,
                         "sats": sats,
                         "alt": alt }


def radio_handler(radioqueue, radio):
  while True:
    while radioqueue['out'].qsize() > 0:
      outmsg = radioqueue['out'].get()
      # FIXME: Will we ever actually send raw packets out from this thread?
    if radio.rx_dr():
      inmsg = "".join(map(chr, radio.r_rx_payload()))
      if not len(inmsg) == 3:
        continue #Sometimes messages get truncated. Ignore them.
      radioqueue['in'].put(inmsg)


def menuaction(menuitem, args):
  global state
  global stateset
  global diffmode
  global pickfile
  action = args[0]
  debug = args[1]
  if action == "changestate":
    headunit = args[2]
    newstate = args[3]
    if debug >= 1: print(">RECV> ??? READY ???: {NEW MODE: " + newstate + "} {DIFF MODE: " + diffmode + "}")
    state = newstate
    stateset = time.time()

  elif action == "ghostmodequery":
    if debug >= 1: print (">>>> Query ghost mode: " + diffmode)
    for i in menuitem['submenu']:
      if i['label'] == diffmode:
        i['labelcolor'] = "green"
      else:
        i['labelcolor'] = "yellow"

  elif action == "refreshghostlist":
    menuitem['submenu'] = [];
    sessionid = 0
    for sessionfile in sorted(os.listdir("./data")):
      if sessionfile.endswith(".dat"):
        sessionid += 1
        menuitem['submenu'].append({'label': str(sessionid),
                                    'labeltype': 'string',
                                    'dofunction': menuaction,
                                    'do_args': ['pickghost', debug, sessionfile],
                                    'backbutton': 'true'})
    menuitem['submenu'].append({'label': 'goback',
                                'labeltype': 'pixart',
                                'backbutton': 'true'})
    if debug >= 1: print (">>>> Refreshed ghost picklist: {:d} found".format(sessionid))

  elif action == "pickghost":
    pickfile = args[2]
    diffmode = 'PIK'
    if debug >= 1: print (">>>> Picked ghost file: [{:s}]".format(pickfile))

  elif action == "setghostmode":
    diffmode = menuitem['label']
    pickfile = None
    if debug >= 1: print (">>>> Set ghost mode: " + menuitem['label'])

  return menuitem

def mainthread():
  global state
  global stateset
  global diffmode
  global pickfile

  # Set to zero to turn off
  debug = 2


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
  headunit.menu.tree[0]['do_args'] = [ 'changestate', debug, headunit, "makeready" ]
  headunit.menu.tree[2]['dofunction'] = menuaction
  headunit.menu.tree[2]['do_args'] = [ 'ghostmodequery', debug ]
  headunit.menu.tree[2]['submenu'][0]['dofunction'] = menuaction
  headunit.menu.tree[2]['submenu'][0]['do_args'] = [ 'refreshghostlist', debug ]
  headunit.menu.tree[2]['submenu'][1]['dofunction'] = menuaction
  headunit.menu.tree[2]['submenu'][1]['do_args'] = [ 'setghostmode', debug ]
  headunit.menu.tree[2]['submenu'][2]['dofunction'] = menuaction
  headunit.menu.tree[2]['submenu'][2]['do_args'] = [ 'setghostmode', debug ]

  headunit.drawCurrentMenuItem()

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
          ])
  evtmgr.stopList.extend(
          [
              recorder.stopInstance,
          ])
  #evtmgr.updateList.extend(
  #        [
  #            gpio.handleEvents,
  #        ])

  print("Initialized!\n- - - - - - - - - - - -")

  while True:

    if radioqueue['in'].qsize() > 0:
      inmsg = radioqueue['in'].get()
      if inmsg == "P10":
        if debug >= 3: print(">RECV> Ping from headunit: {re-sent buffer}")
        headunit.sendBuffer()

      elif state == "menu" and inmsg[0] == "B" and inmsg[2] == '1':
        if inmsg[1] == '1': # Red button
          if debug >= 1: print(">RECV> Red button: {menu-up}")
          headunit.menuAction('up')
        elif inmsg[1] == '2': # Green button
          if debug >= 1: print(">RECV> Green button: {menu-down}")
          headunit.menuAction('down')
        elif inmsg[1] == '3': # Yellow button
          if debug >= 1: print(">RECV> Yellow button: {menu-select}")
          headunit.menuAction('select')

      # Cancel ready mode
      elif state == "ready" and inmsg == "B11" and (time.time() - stateset > 0.5):
        if debug >= 1: print(">RECV> Red button: {Cancel ready-mode, NEW MODE: menu}")
        state = "menu"
        stateset = time.time()
        headunit.drawCurrentMenuItem()

      # GO!
      elif state == "ready" and (inmsg == "I21" or inmsg == "B21") and (time.time() - stateset > 0.5):
        if debug >= 1: print(">RECV> !!! GO !!!: {NEW MODE: run}")
        evtmgr.doStartEvent();
        state = "run"
        stateset = time.time()

      # STOP!
      elif state == "run" and (inmsg == "I31" or inmsg.startswith("B")) and (time.time() - stateset > 1):
        if debug >= 1:
          print(">RECV> ### STOP ###: {NEW MODE: postrun}")
          print("       Why?: {:s}, Delta: {:.2f}".format("Button" if inmsg.startswith("B") else "Beam", time.time() - stateset))
        evtmgr.doStopEvent();
        state = "postrun"
        stateset = time.time()
        headunit.display.floodColor('B')
        headunit.display.drawString('POST', 0, 1, 'R')
        headunit.sendBuffer()

    # Super-kludgy way to do screen changes on state change
    #if time.time() - stateset < 0.5:
    #  if state == "ready":
    #    headunit.display.floodColor('B')
    #    headunit.display.drawString('RDY!', 0, 1, 'Y')
    #    headunit.sendBuffer()
    #  elif state == "run":
    #    headunit.display.floodColor('B')
    #    headunit.display.drawString('!GO!', 0, 1, 'G')
    #    headunit.sendBuffer()
    #  elif state == "postrun":
    #    headunit.display.floodColor('B')
    #    headunit.display.drawString('POST', 0, 1, 'R')
    #    headunit.sendBuffer()

    if state == "makeready":
      if diffmode == "PIK" and pickfile:
        gfile = open("data/{:s}".format(pickfile), 'r')
        recorder.ghost = json.loads(gfile.read())
        if debug >= 1: print(">>>> Loaded {:s} ghost: {:s}".format(diffmode, gfile.name))
      elif diffmode == "PRV":
        gfile = open("data/{:s}".format(sorted(os.listdir("./data"))[-1]), 'r')
        recorder.ghost = json.loads(gfile.read())
        if debug >= 1: print(">>>> Loaded {:s} ghost: {:s}".format(diffmode, gfile.name))
      elif diffmode == "OFF":
        recorder.ghost = None

      headunit.display.floodColor('B')
      headunit.display.drawString('RDY!', 0, 1, 'Y')
      headunit.sendBuffer()
      state = "ready"
      stateset = time.time()
      if debug >= 1: print(">:>:>:> NEW MODE: ready")

    if state == "postrun" and time.time() - stateset > 5:
      state = "menu"
      stateset = time.time()
      headunit.drawCurrentMenuItem()

    if gpsdata["GGA"] and recorder.active:
      i = gpsdata["GGA"]
      recorder.update(gps = {"lat": i['lat'], "lon": i['lon'], "alt": i['alt']})
      if recorder.ghost:
        delta = recorder.store[-1]["points"][-1]["delta"]
        if delta > 0.1:
          c = 'R'
        elif delta >= -0.1:
          c = 'Y'
        else:
          c = 'G'
        headunit.display.floodColor('B')
        headunit.display.drawString('{:4.1f}'.format(delta), 0, 1, c)
        headunit.sendBuffer()
      else:
        elapsed = recorder.store[-1]["points"][-1]["sessiontime"]
        headunit.display.floodColor('B')
        headunit.display.drawString('{:4.1f}'.format(elapsed), 0, 1, 'Y')
        headunit.sendBuffer()
      gpsdata['GGA'] = None


    #FIXME Do we even need this any more? Where does it go?
    #evtmgr.doUpdateEvent()

    time.sleep(0.01)   # Burn less CPU


if __name__ == "__main__":
  mainthread()
