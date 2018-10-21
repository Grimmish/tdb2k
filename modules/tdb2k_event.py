class tdb2k_event:
    def __init__(self):
        self.startList = []
        self.stopList = []
        self.updateList = []

    def doStartEvent(self):
        for evt in self.startList:
            evt()

    def doStopEvent(self):
        for evt in self.stopList:
            evt()

    def doUpdateEvent(self):
        for evt in self.updateList:
            evt()

