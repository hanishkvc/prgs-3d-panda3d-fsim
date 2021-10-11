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


def parse_aptdat(sFName):
    f = open(sFName, errors='replace')
    state = '0'
    lCnt = 0
    for l in f:
        lCnt += 1
        l = l.strip()
        la = cleanup_line(l)
        if len(la) == 0:
            state = '0'
            lat = None
            lon = None
            continue
        else:
            if gbDebug:
                print("DBUG:ParseAptDat:{}:{}".format(lCnt,la))
        if la[0] == "1":
            if state != '0':
                print("ERRR:ParseAptDat:{}:New Airport Line before ending of prev airport data?".format(lCnt))
                continue
            state = 'A'
            print("INFO:A:", la[4], la[5:])
        elif la[0] == "100":
            if state != 'A':
                print("ERRR:ParseAptDat:{}:Runway data in wrong place?".format(lCnt))
                continue
            print("INFO:R:", la[9], la[10])
        else:
            continue


parse_aptdat(sys.argv[1])

