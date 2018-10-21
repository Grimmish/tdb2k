#!/usr/bin/python

# Remember to set PYTHONPATH to find custom modules

import Tkinter as tk
from tkFont import Font
import serial
import time

import gpshelp
import tdb2k_event
import tdb2k_data

import wiringpi2 as wpi

class tdb2k_gpio:
    def __init__(self, startPin, startAction, stopPin, stopAction):
        wpi.wiringPiSetup()
        wpi.pinMode(startPin, wpi.GPIO.INPUT)
        wpi.pullUpDnControl(startPin, wpi.GPIO.PUD_UP)
        wpi.wiringPiISR(startPin, wpi.GPIO.INT_EDGE_FALLING, self.startTrigger)
        wpi.pinMode(stopPin, wpi.GPIO.INPUT)
        wpi.pullUpDnControl(stopPin, wpi.GPIO.PUD_UP)
        wpi.wiringPiISR(stopPin, wpi.GPIO.INT_EDGE_FALLING, self.stopTrigger)

        self.startAction = startAction
        self.stopAction = stopAction
        self.newEvent = False
        self.latestEvent = ''

    def startTrigger(self):
        if self.latestEvent != 'start':
            self.latestEvent = 'start'
            self.newEvent = True

    def stopTrigger(self):
        if self.latestEvent != 'stop':
            self.latestEvent = 'stop'
            self.newEvent = True

    def handleEvents(self):
        if not self.newEvent:
            return

        print(self.latestEvent)
        self.newEvent = False
        if self.latestEvent == 'start':
            return self.startAction()
        elif self.latestEvent == 'stop':
            return self.stopAction()

        return None


class tdb2k_display(tk.Frame):
    def startTime(self):
        self.timerbox["fg"] = "green"
        self.currentMode.set("run")
        self.elapsed = 0.0
        self.anchorTime = time.time()
        self.update_timing()

    def stopTime(self):
        self.timerbox["fg"] = "red"
        self.currentMode.set("stop")
        self.update_timing()

    def update_timing(self):
        if self.currentMode.get() == "run":
            self.elapsed = time.time() - self.anchorTime
            self.timer.set("%03.1f" % self.elapsed)

    def buildFrameStack(self):
        for i in [ "s1", "s2", "s3" ]:
            self.zones[i] = tk.Frame(self,
                                     borderwidth=5,
                                     relief=tk.SUNKEN,
                                     height=200,
                                     width=200)

        self.zones["s1"]["background"] = "blue"
        self.zones["s1"].place(x=0, y=0)

        self.zones["s2"]["background"] = "green"
        self.zones["s2"].place(x=0, y=200)

        self.zones["s3"]["background"] = "red"
        self.zones["s3"].place(x=0, y=400)

        self.b_QUIT = tk.Message(self.zones["s1"],
                                 textvariable = self.currentMode,
                                 font = self.buttonfont,
                                 bg = "#111155",
                                 fg = "#9999ff",
                                 width = 200)
        self.b_QUIT.place(relx=0.5, rely=0.5, anchor="c")

        self.b_launch = tk.Button(self.zones["s2"],
                                  text = "Go!",
                                  font = self.buttonfont,
                                  bg = "#115511",
                                  fg = "#99ff99",
                                  command = self.startLatch)
        self.b_launch.place(relx=0.5, rely=0.5, anchor="c")

        self.b_finish = tk.Button(self.zones["s3"],
                                  text = "Done!",
                                  font = self.buttonfont,
                                  bg = "#551111",
                                  fg = "#ffff99",
                                  command = self.stopLatch)
        self.b_finish.place(relx=0.5, rely=0.5, anchor="c")

    def buildFramePrime(self):
        self.zones["p1"] = tk.Frame(self,
                                    background = "black",
                                    borderwidth=5,
                                    relief=tk.SUNKEN,
                                    width=824,
                                    height=400)
        self.zones["p1"].place(x=200, y=0)

        self.zones["p2"] = tk.Frame(self,
                                    background = "#9999ff",
                                    borderwidth=5,
                                    relief = tk.SUNKEN,
                                    width = 824,
                                    height = 200)
        self.zones["p2"].place(x=200, y=400)

        self.timerbox = tk.Message(self.zones["p1"],
                                   font = self.megafont,
                                   justify = "center",
                                   fg = "white",
                                   bg = "black",
                                   textvariable = self.timer,
                                   width=800)
        self.timerbox.place(relx=0.5, rely=0.5, anchor="c")

        self.foo = tk.Message(self.zones["p2"],
                              justify = "left",
                              width=800,
                              textvariable = self.foovar)
        self.foo.place(relx=0.0, rely=0.0, anchor="nw")


    def createLayout(self):
        self.buildFrameStack()
        self.buildFramePrime()

        
    def __init__(self, master=None, startLatch=None, stopLatch=None):
        tk.Frame.__init__(self, master, width=1024, height=600)
        self.pack(fill=None, expand=False)

        self.zones = {}
        self.buttonfont = Font(family="ledfixed", size=30)
        self.megafont = Font(family="ledfixed", size=150, weight="bold")
        self.timer = tk.StringVar()
        self.timer.set("--.-")
        self.foovar = tk.StringVar()
        self.foovar.set("? ? ? ?")
        self.bmatest = 2

        self.currentMode = tk.StringVar()
        self.elapsed = 0.0
        self.anchorTime = None

        # Be sure to define these after instantiating the class
        self.startLatch = startLatch
        self.stopLatch = stopLatch

        self.createLayout()



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
            stopLatch=evtmgr.doStopEvent
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
                window.stopTime
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

            window.foovar.set('Sats: %d    Qual: %s    Fixtime: %s\nRun instance: %d' % (sats,qual,str(fixtime)[:21], recorder.instance))
            evtmgr.doUpdateEvent()
            recorder.update(gps = {"fixtime": fixtime, "lat": lat, "lon": lon, "alt": alt})

