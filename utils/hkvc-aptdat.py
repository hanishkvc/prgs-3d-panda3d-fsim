#!/usr/bin/env python3
# Work on apt.dat from FlightGear/XPlane
# HanishKVC, 2021
# GPL


import sys


gbDebug = False


def cleanup_line(sL):
    la = []
    prev = ''
    for cur in sL:
        if cur == ' ':
            if prev == '':
                continue
            else:
                la.append(prev)
                prev = ''
        else:
            prev += cur
    if prev != '':
        la.append(prev)
    return la


def parse_aptdat(sFName, db):
    f = open(sFName, errors='replace')
    state = '0'
    lCnt = 0
    apt = {}
    for l in f:
        lCnt += 1
        l = l.strip()
        la = cleanup_line(l)
        if len(la) == 0:
            state = '0'
            if apt.get('lat'):
                k = "{:6.2f}-{:6.2f}".format(float(apt['lat']),float(apt['lon']))
                db[k] = apt
            apt = {}
            continue
        else:
            if gbDebug:
                print("DBUG:ParseAptDat:{}:{}".format(lCnt,la))
        if la[0] == "1":
            if state != '0':
                print("ERRR:ParseAptDat:{}:New Airport Line before ending of prev airport data?".format(lCnt))
                continue
            state = 'A'
            apt['icao'] = la[4]
            if gbDebug:
                print("INFO:A:", la[4], la[5:])
        elif la[0] == "100":
            if state != 'A':
                print("ERRR:ParseAptDat:{}:Runway data in wrong place?".format(lCnt))
                continue
            if gbDebug:
                print("INFO:R:", la[9], la[10])
            if not apt.get('lat'):
                apt['lat'] = la[9]
                apt['lon'] = la[10]
        else:
            continue


gDB = {}
parse_aptdat(sys.argv[1], gDB)
print(gDB)

