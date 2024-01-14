import serial
import time
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# SERIAL
ser1 = serial.Serial('COM7',115200)
ser1.timeout = 5
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
stepx = 1
stepy = 1
stepz = 1

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

# run data collection algorithm, get quiver plot
ldata = [[],[],[]]
lpos = [[],[],[]]
def getdata():
    global updates,range_x,range_y,range_z, stepx, stepy, stepz
    updates = "collecting data"
    global ldata, lpos
    ldata = [[],[],[]]
    lpos = [[],[],[]]

    # define measurement ranges
    # multiplied by 100 to account for floats
    rxi = int(range_x*100)
    ryi = int(range_y*100)
    rzi = int(range_z*100)
    if not (rxi and ryi and rzi):
        print("One or more ranges empty")
        return()
    
    # add step size for measurement increments
    stepx = int(stepx*100)
    stepy = int(stepy*100)
    stepz = int(stepz*100)

    # include outer bounds
    # rx = (rxi+stepx)-(rxi%stepx)+(stepx*int(rxi%stepx != 0))
    # ry = (ryi+stepy)-(ryi%stepy)+(stepy*int(ryi%stepy != 0))
    # rz = (rzi+stepz)-(rzi%stepz)+(stepx*int(rzi%stepz != 0))

    # don't include outer bounds
    rx = (rxi)-(rxi%stepx)+(stepx*int(rxi%stepx != 0))
    ry = (ryi)-(ryi%stepy)+(stepy*int(ryi%stepy != 0))
    rz = (rzi)-(rzi%stepz)+(stepx*int(rzi%stepz != 0))

    # c = [2,xc,yc,zc]

    # move steppers to bottom left
    zero()
    print("zeroed")
    c = [2,-(rxi/100)/2,0,-(rzi/100)/2]
    c = [str(i) for i in c]
    print("moving to bottom left:",c)
    ser1.write(bytes(",".join(c), 'utf-8'))
    print("moved",readser())
    # wait_(1)
    zero()
    # wait_(1)
    c = [2,0,0,0]

    # collect data
    reverse = False
    revx = False
    if (rz//stepz) % 2 == 1:
        revx = True
    xc = 0
    yc = 0
    zc = 0
    print("starting algorithm")
    for i in range(0,ry,stepy):
        yc = i
        for j in range(0,rz,stepz):
            if (i/stepy)%2 == 0:
                zc = j
                reverse = False
            elif (i/stepy)%2 == 1:
                zc = rz-j-stepz
                reverse = True
            for k in range(0,rx,stepx):
                if (j/stepz)%2==0:
                    xc = k
                elif (j/stepz)%2 == 1:
                    xc = rx-k-stepx
                if reverse and revx:
                    xc = rx-xc-stepx

                c = [2,xc/100,-yc/100,zc/100]
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
                ldata[0].append(float(r[0]))
                ldata[1].append(float(r[1]))
                ldata[2].append(float(r[2]))
                # lpos.append(c[1:])
                lpos[0].append(float(c[1]))
                lpos[1].append(-float(c[2]))
                lpos[2].append(float(c[3]))

                # wait_(1.5)

    print(type(ldata[0][0]))
    print(type(lpos[0][0]))
    print(ldata)
    print(lpos)

    # create colormap
    color_strengths = []
    for n in range(len(ldata[0])):
        a = ldata[0][n]
        b = ldata[1][n]
        c = ldata[2][n]
        strength = np.sqrt(a**2+b**2+c**2)
        color_strengths.append(strength)
    color_scalars = []
    a = np.min(color_strengths)
    b = np.max(color_strengths)
    for i in color_strengths:
        color_scalars.append((i - a) / (b-a))

    ncs = color_scalars.copy() # for arrowheads
    for i in color_scalars:
        ncs.append(i)
        ncs.append(i)

    ax = plt.figure().add_subplot(projection='3d')
    cmap = plt.get_cmap()
    ax.quiver(lpos[0], lpos[1], lpos[2], ldata[0], ldata[1], ldata[2], color=cmap(ncs), normalize=True, pivot='middle')
    plt.show()

    updates = "done collecting. not doing anything"

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
    elif s == "2":
        x = 1
        y = 1
        z = 1
        a = time.time()
        moveto()
        print(time.time()-a)
    elif s == "3":
        range_x = 5
        range_y = 1
        range_z = 1
        stepx = 0.5
        stepy = 1
        stepz = 1
        getdata()
        # print(ldata)
        # print(lpos)
    elif s != "":
        print(s)
        a = time.time()
        ser1.write(bytes(s, 'utf-8'))
        print("wrote",readser())
        print(time.time()-a)


