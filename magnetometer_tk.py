import serial
import time
import tkinter as tk
# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import string

# note: do NOT comment out print statements with readser() 

# SERIAL
ser1 = serial.Serial('COM7',115200)
ser1.timeout = 5
# time.sleep(1)

# GUI window & stringvars
win = tk.Tk()
updates = tk.StringVar()
updates.set("No operations running.")
pos = tk.StringVar()
tmag = tk.StringVar()
data_collected = tk.StringVar()
pos.set("Position: Not found | Target: Not found")
tmag.set("Magnet data here")
x = 0
y = 0
z = 0
range_x = 0
range_y = 0
range_z = 0
step_x = 1
step_y = 1
step_z = 1

# time.sleep mimic (unused)
def wait_(s):
    time1 = time.time()
    time2 = time.time()
    while time2-time1 < s:
        time2 = time.time()
        # print(time2-time1)
    
def readser():
    global ser1, pos
    # ser1.write(bytes("3,0,0,0", 'utf-8'))
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
    pos.set(posdata)
    tmag.set(magdata)
    return([magdata,posdata])

def reqser():
    ser1.write(bytes("3,", 'utf-8'))
    print(readser())

def zero():
    global updates
    updates.set("Zeroing")
    # o = [1,0,0,0]
    # o = [str(i) for i in o]
    # ser1.write(bytes(",".join(o), 'utf-8'))
    ser1.write(bytes("1,", 'utf-8'))
    print("Zeroed",readser())
    updates.set("Done zeroing.")

# move given movement amount, not absolute position
def moveto():
    global updates,x,y,z
    updates.set("moving")
    o = [2,x.get(),y.get(),z.get()]
    print("values received:",o)
    ser1.write(bytes('3,','utf-8'))
    currentpos = readser()[1]
    # print("got current position")
    currentpos = currentpos[9:].split(" | ")
    currentpos = currentpos[0].split(",")
    for i in range(3):
        currentpos[i] = float(currentpos[i])
    # print("position values to add:",currentpos)
    for i in range(4):
        if o[i] == '':
            o[i] = 0
        o[i] = float(o[i])
    for i in range(3):
        o[i+1] += currentpos[i]
    o = [str(i) for i in o]
    o.append(',')
    # print("new values to move to:",o)
    ser1.write(bytes(",".join(o), 'utf-8'))
    # wait_(1)
    print("Moved",readser())
    updates.set("Moved.")

# run data collection algorithm, get quiver plot
ldata = [[],[],[]]
lpos = [[],[],[]]
def getdata():
    global updates,range_x,range_y,range_z, step_x, step_y, step_z
    updates.set("Collecting data")
    global ldata, lpos

    ldata = [[],[],[]]
    lpos = [[],[],[]]

    if not (range_x and range_y and range_z and step_x and step_y and step_z):
        updates.set("Can't collect data, one or more ranges or increment sizes empty")
        return()

    # print("ranges:",range_x.get(),range_y.get(),range_z.get())
    # print("steps:",step_x.get(),step_y.get(),step_z.get())

    # define measurement ranges
    # multiplied by 100 to account for floats
    rxi = int(float(range_x.get())*100)
    ryi = int(float(range_y.get())*100)
    rzi = int(float(range_z.get())*100)
    
    # add step size for measurement increments
    stepx = int(float(step_x.get())*100)
    stepy = int(float(step_y.get())*100)
    stepz = int(float(step_z.get())*100)

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
    c = [2,-(rxi/100)/2,0,-(rzi/100)/2,","]
    print(c)
    c = [str(i) for i in c]
    print("Moving to bottom left:",c)
    ser1.write(bytes(",".join(c), 'utf-8'))
    print("Moved to bottom left",readser())
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
    print("Starting algorithm")
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

                c = [2,xc/100,-yc/100,zc/100,","]
                c = [str(i) for i in c]
                print(c)
                ser1.write(bytes(",".join(c), 'utf-8'))
                # wait_(1)
                print("printing data")
                r = readser()
                r = r[0]
                print(r)

                # add measurement to ldata
                r = r.split(", ")
                ldata[0].append(float(r[0]))
                ldata[1].append(float(r[1]))
                ldata[2].append(float(r[2]))
                lpos[0].append(float(c[1]))
                lpos[1].append(-float(c[2]))
                lpos[2].append(float(c[3]))

                # wait_(1.5)

    # move back to center
    c = [2,(rxi/100)/2,0,(rzi/100)/2,","]
    # print(c)
    c = [str(i) for i in c]
    # print("Moving back to center:",c)
    ser1.write(bytes(",".join(c), 'utf-8'))
    print("Moved back to center",readser())
    # wait_(1)
    # zero()

    # write data to text file with random name
    filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))    
    filename = r"c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\\" + filename + ".txt"
    f = open(filename,'a')
    f.write('\n'.join([', '.join([str(n) for n in ldata[i]]) for i in range(3)]))
    f.write('\n')
    f.write('\n'.join([', '.join([str(n) for n in lpos[i]]) for i in range(3)]))
    f.close()

    # print(ldata)
    # print(lpos)

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
    print("Max field strength:", b)
    for i in color_strengths:
        color_scalars.append((i - a) / (b-a))

    ncs = color_scalars.copy() # for arrowheads
    for i in color_scalars:
        ncs.append(i)
        ncs.append(i)

    # make alpha a little higher so it's not too transparent
    transparencies = ncs.copy()
    for i in range(len(transparencies)):
        val = transparencies[i]
        transparencies[i] = val + 0.25
        if transparencies[i] > 1:
            transparencies[i] = 1

    # make quiver plot
    ax = plt.figure().add_subplot(projection='3d')
    cmap = plt.get_cmap('plasma')
    maxlen = min(stepx/100,stepy/100,stepz/100)
    ax.quiver(lpos[0], lpos[1], lpos[2], ldata[0], ldata[2], [-i for i in ldata[1]], color=cmap(ncs), normalize=True, pivot='middle', length = maxlen, alpha = transparencies)
    maxrange = max(rxi/100,ryi/100,rzi/100)
    ax.set_xlim(0,maxrange)
    ax.set_ylim(0,maxrange)
    ax.set_zlim(0,maxrange)
    
    plt.show()

    updates.set("Done collecting.")

# GUI
# win.geometry("800x700")
tk.Label(win,text="Magnetometer Control Panel").pack()
tk.Label(win,textvariable=pos).pack()
tk.Label(win,textvariable=tmag).pack()
tk.Label(win,textvariable=updates).pack()
reqser() # populate data

refresh = tk.Button(text="Refresh Data",command=reqser).pack()

tk.Label(win,text="\nMove").pack()
tk.Label(win,text="Enter movement amount in mm (not absolute position!) for X, Y, Z").pack()
tk.Label(win,text="X").pack()
x = tk.Entry(win)
x.pack()
tk.Label(win,text="Y").pack()
y = tk.Entry(win)
y.pack()
tk.Label(win,text="Z").pack()
z = tk.Entry(win)
z.pack()
run = tk.Button(text="Run",command=moveto).pack()
zero_button = tk.Button(text="Zero",command=zero).pack()


tk.Label(win,text="\nData Collect").pack()
tk.Label(win,text="\nPosition at center front face of measurement range (closest to the magnet).").pack()
dataf = tk.Frame(win)
dataf.pack()
tk.Label(dataf,text="X Range").grid(row=0,column=0)
range_x = tk.Entry(dataf)
range_x.grid(row=1,column=0)
tk.Label(dataf,text="X Step").grid(row=0,column=1)
step_x = tk.Entry(dataf)
step_x.grid(row=1,column=1)
tk.Label(dataf,text="Y Range").grid(row=2,column=0)
range_y = tk.Entry(dataf)
range_y.grid(row=3,column=0)
tk.Label(dataf,text="Y Step").grid(row=2,column=1)
step_y = tk.Entry(dataf)
step_y.grid(row=3,column=1)
tk.Label(dataf,text="Z Range").grid(row=4,column=0)
range_z = tk.Entry(dataf)
range_z.grid(row=5,column=0)
tk.Label(dataf,text="Z Step").grid(row=4,column=1)
step_z = tk.Entry(dataf)
step_z.grid(row=5,column=1)
rundata = tk.Button(win,text="Run Data Collect",command=getdata).pack()

# optional 'while loop' could be used for continuously updating data while stationary
# loops_elapsed = 0
# def gotime():
#     global loops_elapsed

#     loops_elapsed += 1

#     win.after(1,gotime)

# win.after(1000,gotime)
win.mainloop()

