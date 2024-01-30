import matplotlib.pyplot as plt
import numpy as np

ax = plt.figure().add_subplot(projection='3d')

# read data from file
magdata = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\VC67I.txt','r')
def getfiledata():
    initial = magdata.readline().strip().split(', ')
    return [float(i) for i in initial]

u = getfiledata()
v = getfiledata()
w = getfiledata()
x = getfiledata()
y = getfiledata()
z = getfiledata()

# print(u,v,w,x,y,z)

# can also manually enter data to test
# x = [0,1,2,3,4]
# y = [0,0,0,0,0]
# z = [0,0,0,0,0]

# u = [0,0,0,0,0]
# v = [1,1,5,1,2]
# w = [-1,-10,-1,-1,-4]

# create colormap
color_strengths = []
for i in range(len(u)):
    a = u[i]
    b = v[i]
    c = w[i]
    size = np.sqrt(a**2+b**2+c**2)
    u[i] = a/size
    v[i] = b/size
    w[i] = c/size
    color_strengths.append(size)

color_scalars = []
a = np.min(color_strengths)
b = np.max(color_strengths)
for i in color_strengths:
    color_scalars.append((i - a) / (b-a))

ncs = color_scalars.copy()
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

# print(color_strengths)
# print(color_scalars)

# FIND CENTER
col_xstrengths = {}
row_ystrengths = {}
# print(len(x))
# print(max(y))
for i in range(int(len(x)//(max(y)+1))):
    # print(x[i],y[i],z[i])
    if x[i] in col_xstrengths.keys():
        col_xstrengths[x[i]] += abs(u[i])
    else:
        col_xstrengths[x[i]] = abs(u[i])
    if z[i] in row_ystrengths.keys():
        row_ystrengths[z[i]] += abs(v[i])
    else:
        row_ystrengths[z[i]] = abs(v[i])
    
# print(col_xstrengths)
bestcol = list(col_xstrengths.keys())[list(col_xstrengths.values()).index(min(col_xstrengths.values()))]
print(bestcol)
# print(row_ystrengths)
bestrow = list(row_ystrengths.keys())[list(row_ystrengths.values()).index(min(row_ystrengths.values()))]
print(bestrow)

# plot the data
cmap = plt.get_cmap('plasma')
ax.quiver(x, y, z, u, w, [-i for i in v], color=cmap(ncs), pivot='middle', length=0.5, alpha=transparencies)
maxrange = max(max(x),max(y),max(z))
ax.set_xlim(0,maxrange)
ax.set_ylim(0,maxrange)
ax.set_zlim(0,maxrange)

plt.show()
# save file as PDF for high resolution

