import serial
import time
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# SERIAL
ser1 = serial.Serial('COM7',115200)
ser1.timeout = 0
# time.sleep(1)

# GUI window & stringvars
pos = "Position: not found | Target: not found"
tmag = "magnet data here"
x = 0
y = 0
z = 0
range_x = 0
range_y = 0
range_z = 0

# time.sleep mimic
def wait_(s):
    time1 = time.time()
    time2 = time.time()
    while time2-time1 < s:
        time2 = time.time()
        # print(time2-time1)

def readser():
    global ser1, pos
    # ser1.write(bytes("3", 'utf-8'))
    while True:
        line1 = str(ser1.readline())
        line2 = str(ser1.readline())
        # print(line1,line2)
        if any(i.isdigit() for i in line1) and any(i.isdigit() for i in line2):
            break
        wait_(0.001)
    magdata = ""
    posdata = ""
    if len(line1) > len(line2):
        magdata = (str(line2)[2:-5])
        posdata = (str(line1)[2:-3])
    elif len(line2)>len(line1):
        magdata = (str(line1)[2:-5])
        posdata = (str(line2)[2:-3])
    pos = posdata
    tmag = magdata
    return([magdata,posdata])

# print(readser())
# print(ser1.readline())

def zero():
    global updates
    print("zeroing")
    o = [1,0,0,0]
    o = [str(i) for i in o]
    ser1.write(bytes(",".join(o), 'utf-8'))
    updates = "done zeroing."
    print("zeroed",readser())

# move given movement amount, not absolute position
def moveto():
    global updates,x,y,z
    updates = "moving"
    o = [2,x,y,z]
    # print("values received:",o)
    ser1.write(bytes("3", 'utf-8'))
    print("got current position")
    currentpos = readser()[1]
    currentpos = currentpos[9:].split(" | ")
    currentpos = currentpos[0].split(",")
    for i in range(3):
        currentpos[i] = float(currentpos[i])
    print("position values to add:",currentpos)
    for i in range(4):
        if o[i] == '':
            o[i] = 0
        o[i] = float(o[i])
    for i in range(3):
        o[i+1] += currentpos[i]
    o = [str(i) for i in o]
    print("new values to move to:",o)
    ser1.write(bytes(",".join(o), 'utf-8'))
    # wait_(1)
    updates = "done moving."
    print("moved",readser())

# run data collection algorithm, return data list
ldata = [[],[],[]]
lpos = [[],[],[]]
def getdata():
    global updates,range_x,range_y,range_z
    updates = "collecting data"
    global ldata, lpos
    time1 = time.time()
    rx = range_x
    ry = range_y
    rz = range_z
    if not (rx and ry and rz):
        return()
    ldata = [[],[],[]]
    lpos = [[],[],[]]
    # need to add adjustable step increment size per measurement
    # (right now it's static at 1mm)
    rx = int(rx)
    ry = int(ry)
    rz = int(rz)

    xc = 0
    yc = 0
    zc = 0
    # c = [2,xc,yc,zc]

    zero()
    print("zeroed")
    c = [2,-rx/2,0,-rz/2] # move steppers to bottom left
    c = [str(i) for i in c]
    print("moving to bottom left:",c)
    ser1.write(bytes(",".join(c), 'utf-8'))
    print("moved",readser())
    # wait_(1)
    zero()
    # wait_(1)
    c = [2,0,0,0]

    reverse = False

    print("starting algorithm")
    for i in range(int(ry)):
        yc = i
        for j in range(int(rz)):
            if i%2 == 0:
                zc = j
                reverse = False
            elif i%2 == 1:
                zc = rz-j-1
                reverse = True
            for k in range(int(rx)):
                if j%2==0:
                    xc = k
                elif j%2 == 1:
                    xc = rx-k-1
                if(reverse):
                    xc = rx-xc-1

                c = [2,xc,-yc,zc]
                c = [str(i) for i in c]
                print(c)
                ser1.write(bytes(",".join(c), 'utf-8'))
                # wait_(1)
                print("printing data")
                r = readser()
                r = r[0]
                print(r)

                # add measurement to ldata
                # ldata.append(r)
                r = r.split(", ")
                ldata[0].append(int(r[0]))
                ldata[1].append(int(r[1]))
                ldata[2].append(int(r[2]))
                # lpos.append(c[1:])
                lpos[0].append(int(c[1]))
                lpos[1].append(int(c[2]))
                lpos[2].append(int(c[3]))

                # wait_(1.5)
    updates = "done collecting. not doing anything"

    print(type(ldata[0][0]))
    print(type(lpos[0][0]))
    print(ldata)
    print(lpos)


    colors = []
    for n in range(len(ldata[0])):
        a = ldata[0][n]
        b = ldata[1][n]
        c = ldata[2][n]
        strength = np.sqrt(a**2+b**2+c**2)


    ax = plt.figure().add_subplot(projection='3d')
    ax.quiver(lpos[0], lpos[1], lpos[2], ldata[0], ldata[1], ldata[2], length=0.1, normalize=True, pivot='mid')
    plt.show()



def test_time():
    # zero()
    # print("zeroed")
    # o = ['2','1','0','0']
    # ser1.write(bytes(",".join(o), 'utf-8'))
    ser1.write(bytes("3", 'utf-8'))
    print("Wrote")
    t1 = time.time()
    s = readser()
    elapsed = time.time()-t1
    print(s)
    print("time:",elapsed)

while True:
    print("1-zero, 2-test move (zero first), 3-data collect, or enter \"2,x,y,z\" to move.")
    s = input("enter here:")
    if s == "1":
        # print("zero time :)")
        zero()
    if s == "2":
        x = 1
        y = 1
        z = 1
        a = time.time()
        moveto()
        print(time.time()-a)
    elif s == "3":
        range_x = 2
        range_y = 2
        range_z = 2
        getdata()
        print(ldata)
        print(lpos)
    elif s != "":
        print(s)
        a = time.time()
        ser1.write(bytes(s, 'utf-8'))
        print("wrote",readser())
        print(time.time()-a)


