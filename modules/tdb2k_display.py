import Tkinter as tk
from tkFont import Font
import time
import os
import json

class tdb2k_display(tk.Frame):
    def startTime(self):
        self.timerbox["fg"] = "green"
        self.currentStatus.set("run-g" if self.ghost else "run")

    def stopTime(self):
        self.timerbox["fg"] = "red"
        self.currentStatus.set("stop")

    def update_timing(self):
        if self.currentStatus.get().startswith("run"):
          if self.ghost:
            self.timerbox["fg"] = "green" if self.timer.get().startswith("-") else "red"

    def refresh_filepicker(self):
        self.filepicker.delete(0, tk.END)
        for sessionfile in sorted(os.listdir("./data")):
            if sessionfile.endswith(".dat"):
                self.filepicker.insert(tk.END, sessionfile)

    def load_ghost(self):
        selection = self.filepicker.get(tk.ACTIVE)
        try:
            gfile = open("data/%s" % selection, "r")
            self.ghost = json.loads(gfile.read())
            self.currentStatus.set("ghost-rdy")
            self.ghostXfer(self.ghost)

        except:
            print("Kablams while loading file " + ("data/%s" % selection))
            self.currentStatus.set("ghostfail")

    def clear_ghost(self):
        self.ghost = None
        self.ghostXfer(self.ghost)
        self.currentStatus.set("no-ghost")

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
                                 textvariable = self.currentStatus,
                                 font = self.statusfont,
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

        self.filepicker = tk.Listbox(self.zones["p2"],
                                     justify = "left",
                                     width=50,
                                     selectmode = "SINGLE")
        self.filepicker.place(relx=0.0, rely=0.0, anchor="nw")
        self.b_loadghost = tk.Button(self.zones["p2"],
                                     text = "Load",
                                     bg = "#2222aa",
                                     fg = "#bbbbff",
                                     command = self.load_ghost)
        self.b_loadghost.place(relx=0.0, rely=1.0, anchor="sw")
        self.b_clearghost = tk.Button(self.zones["p2"],
                                      text = "Clear",
                                      bg = "#aaaa22",
                                      fg = "#ffffbb",
                                      command = self.clear_ghost)
        self.b_clearghost.place(relx=0.2, rely=1.0, anchor="sw")


    def createLayout(self):
        self.buildFrameStack()
        self.buildFramePrime()

        
    def __init__(self, master=None, startLatch=None, stopLatch=None, ghostXfer=None):
        tk.Frame.__init__(self, master, width=1024, height=600)
        self.pack(fill=None, expand=False)

        self.zones = {}
        self.buttonfont = Font(family="ledfixed", size=30)
        self.statusfont = Font(family="ledfixed", size=20)
        self.megafont = Font(family="ledfixed", size=150, weight="bold")
        self.timer = tk.StringVar()
        self.timer.set("--.-")
        self.bmatest = 2

        self.currentStatus = tk.StringVar()
        self.ghost = None

        # Be sure to define these after instantiating the class
        self.startLatch = startLatch
        self.stopLatch = stopLatch
        self.ghostXfer = ghostXfer

        self.createLayout()
        self.refresh_filepicker()

