import datetime
import time

def parseGPSTime(t):
    # t = '210319.900'
    H = int(t[0:2])
    M = int(t[2:4])
    S = int(t[4:6])
    us = int(t[7:]) * 1000
    return datetime.datetime.combine(datetime.date.today(), datetime.time(H,M,S,us,None))

def polarize(measure, compass):
    # measure = '4427.4581'
    # compass = 'W'
    if compass == 'N' or compass == 'S':
        polar = float(measure[0:2]) + (float(measure[2:]) / 60)
    else:
        polar = float(measure[0:3]) + (float(measure[3:]) / 60)
    if compass == 'W' or compass == 'S':
        polar *= -1
    return polar

def parseRMC(line):
    l = line.split(',')
    fixtime = parseGPSTime(l[1])
    lat = polarize(l[3], l[4])
    lon = polarize(l[5], l[6])
    knots = l[7]
    track = l[8]
    return (fixtime, lat, lon, knots, track)

def parseGGA(line):
    try:
        l = line.split(',')
        fixtime = parseGPSTime(l[1])
        lat = polarize(l[2], l[3])
        lon = polarize(l[4], l[5])
        quality = int(l[6])
        sats = int(l[7])
        alt = float(l[9])
    except:
        return ('', 0, 0, 0, 0, 0)

    return (fixtime, lat, lon, quality, sats, alt)
