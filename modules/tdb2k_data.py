import datetime
import copy
import json
import math
import sys

class tdb2k_data:
    def __init__(self):
        self.store = []
        self.instance = 0
        self.active = False
        self.ghost = None
        self.deltaradius = 50
        self.debug = None
        self.debugfreq = 5

    def prepGhost(self, ghostObj):
        self.ghost = ghostObj

    def startInstance(self):
        # Create other stuff here, too
        self.store.append({
                "launch": str(datetime.datetime.now()),
                "filename": datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.dat"),
                "points": []
                })

        if self.ghost:
            self.store[-1]["ghost"] = self.ghost["filename"]

        self.instance = len(self.store) - 1
        self.epoch = datetime.datetime.now()
        self.active = True

    def stopInstance(self):
        self.active = False
        sessionfile = open("./data/%s" % self.store[-1]["filename"], "w")
        sessionfile.write(json.dumps(self.store[-1], separators=(',',':')))
        sessionfile.close()

    def update(self, gps):
        if not self.active:
            return
        # Do something with it
        self.store[-1]["points"].append(copy.deepcopy(gps))
        sessiontime = (datetime.datetime.now() - self.epoch).total_seconds()
        self.store[-1]["points"][-1]["sessiontime"] = (sessiontime)
        
        if self.ghost:
            self.store[-1]["points"][-1]["delta"] = self.ghostDelta()

    def ghostDelta(self):
        i = len(self.store[-1]["points"])
        range_lo = i-self.deltaradius if i>self.deltaradius else 0
        range_hi = i+self.deltaradius if i+self.deltaradius<len(self.ghost["points"]) else len(self.ghost["points"])-1

        if self.debug and self.debug % self.debugfreq == 1:
            print("- - - - - - - - - - - - - -\nDEBUG: ghostDelta() -- Range: %i:%i" % (range_lo, range_hi))

        #FIXME This should totally be a `reduce` function
        nearest_ghost_index = 0
        nearest_ghost_dist = 1000
        for ghostidx,ghostpoint in enumerate(self.ghost["points"][range_lo:range_hi]):
            dist = self.haversine(self.store[-1]["points"][-1], ghostpoint)
            if self.debug and self.debug % self.debugfreq == 1:
                sys.stdout.write("Ghost-%i vs. %i: %4.0f ft" % (ghostidx+range_lo, i, dist))
            if dist < nearest_ghost_dist:
                nearest_ghost_index = ghostidx+range_lo
                nearest_ghost_dist = dist
                if self.debug and self.debug % self.debugfreq == 1:
                    sys.stdout.write(" ****\n")
            else:
                if self.debug and self.debug % self.debugfreq == 1:
                    sys.stdout.write("\n")

        delta = self.store[-1]["points"][-1]["sessiontime"] - self.ghost["points"][nearest_ghost_index]["sessiontime"] 
        if self.debug:
            self.debug += 1
        return delta

    def haversine(self, a, b): # Each arg is an obj with "lat" and "lon" properties
        # "Haversine" formula:
        #    https://www.movable-type.co.uk/scripts/latlong.html
        earthradius = 6371.0 * 3280.84 # in feet
        lon_delta = math.radians(b["lon"] - a["lon"])
        lat_delta = math.radians(b["lat"] - a["lat"])
    
        a_lat_rad = math.radians(a["lat"])
        b_lat_rad = math.radians(b["lat"])
    
        z = math.sin(lat_delta/2.0)**2 + math.cos(a_lat_rad) * math.cos(b_lat_rad) * math.sin(lon_delta)**2
        c = 2.0 * math.atan2(math.sqrt(z), math.sqrt(1.0-z))
        return c * earthradius

