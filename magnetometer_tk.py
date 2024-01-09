import serial
import time
import tkinter as tk
import pandas as pd
import numpy as np

# SERIAL
ser1 = serial.Serial('COM7',115200)
ser1.timeout = 0.5
time.sleep(1)

# GUI window & stringvars
win = tk.Tk()
updates = tk.StringVar()
updates.set("not doing anything")
pos = tk.StringVar()
tmag = tk.StringVar()
data_collected = tk.StringVar()
pos.set("Position: not found | Target: not found")
tmag.set("magnet data here")

# time.sleep mimic
def wait_(s):
    time1 = time.time()
    time2 = time.time()
    while time2-time1 < s:
        time2 = time.time()
        # print(time2-time1)
    
def readser():
    global ser1, pos
    ser1.write(bytes("3", 'utf-8'))
    line1 = ser1.readline()
    line2 = ser1.readline()
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

# print(readser())
# print(ser1.readline())

def zero():
    global updates
    updates.set("zeroing")
    o = [1,0,0,0]
    o = [str(i) for i in o]
    ser1.write(bytes(",".join(o), 'utf-8'))
    updates.set("done zeroing.")

# move given movement amount, not absolute position
def moveto():
    global updates,x,y,z
    updates.set("moving")
    o = [2,x.get(),y.get(),z.get()]
    print("values received:",o)
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
    wait_(1)
    # updates.set("done moving.")
    updates.set(",".join(o))

# run data collection algorithm, return data list
ldata = []
def getdata():
    global updates,range_x,range_y,range_z
    updates.set("collecting data")
    global ldata
    global data_collected
    time1 = time.time()
    rx = range_x.get()
    ry = range_y.get()
    rz = range_z.get()
    if not (rx and ry and rz):
        updates.set("failed to set range. not doing anything")
        return()
    ldata = []
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
    wait_(1)
    print("zeroed",readser())
    c = [2,-rx/2,0,-rz/2] # move steppers to bottom left
    c = [str(i) for i in c]
    print("moving to bottom left:",c)
    ser1.write(bytes(",".join(c), 'utf-8'))
    print("moved")
    wait_(1)
    print(readser())
    zero()
    wait_(1)
    print("zeroed",readser())
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
                ser1.write(bytes(",".join(c), 'utf-8'))
                print(c)
                
                wait_(1)
                print("printing data")
                r = readser()[0]
                print(r)
 
                # add measurement to ldata
                ldata.append(r)
                data_collected.set(ldata)

                wait_(1.5)
    data_collected.set(ldata)
    updates.set("done collecting. not doing anything")

# GUI
win.geometry("800x700")
tk.Label(win,text="Magnetometer Control Panel").pack()
tk.Label(win,textvariable=pos).pack()
tk.Label(win,textvariable=tmag).pack()
tk.Label(win,textvariable=data_collected).pack()
tk.Label(win,textvariable=updates).pack()

tk.Label(win,text="\nMove").pack()
tk.Label(win,text="Enter movement amount in mm (not absolute position!) for X, Y, Z (starts from bottom left corner)").pack()
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
tk.Label(win,text="\nPosition at front center, then enter range from bottom left").pack()
tk.Label(win,text="X Range").pack()
range_x = tk.Entry(win)
range_x.pack()
tk.Label(win,text="Y Range").pack()
range_y = tk.Entry(win)
range_y.pack()
tk.Label(win,text="Z Range").pack()
range_z = tk.Entry(win)
range_z.pack()
rundata = tk.Button(text="Run Data Collect",command=getdata).pack()
# continue_button = tk.Button("continue")

# t_data = pd.DataFrame(columns=["x","y","z"])
# graph = st.empty()

loops_elapsed = 0
# @st.cache_data
def gotime():
    global loops_elapsed
    # l = readser()
    # pos.set(l[1])
    # # print(line)
    # tmag.set(l[0])

    # tmag_data = l2.split(",")
    # tmag_data = [float(i) for i in tmag_data]
    # t_data.loc[len(t_data)] = tmag_data
    # chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    # if loops_elapsed == 10000:
    #     with graph.container():
    #         # print(t_data)
    #         graph.line_chart(t_data)
    #         # graph.line_chart(chart_data)
    #     loops_elapsed = 0
    # if len(t_data) > 150:
    #     nt = t_data.iloc[1:]
    #     t_data = nt

    loops_elapsed += 1

    # pos.set(str(loops_elapsed))
    win.after(1,gotime)

win.after(1000,gotime)
win.mainloop()

