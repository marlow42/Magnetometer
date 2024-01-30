import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

# read data from file
magdata = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\IORV7.txt','r')
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

print(len(u),len(v),len(w),len(x),len(y),len(z))

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

# ax = plt.figure().add_subplot(projection='3d')
# cmap = plt.get_cmap('jet')
# ax.quiver(x, y, z, u, v, w, color=cmap(ncs), pivot='middle', length=0.5, alpha=transparencies)
# maxrange = max(max(x),max(y),max(z))
# ax.set_xlim(0,maxrange)
# ax.set_ylim(0,maxrange)
# ax.set_zlim(0,maxrange)

xi = np.linspace(0,8,100) # create a linearly spaced array of 100 points between 0 and 24
yi = np.linspace(0,8,100)
zi = griddata((y, z), color_strengths, (xi[None,:], yi[:,None]), method='cubic') # not sure if color_strengths is still raw units from the 5170 but you get the point

colormap = plt.cm.get_cmap('jet')
colors = colormap(color_strengths)
plt.contour(xi, yi, zi, linewidths = 0.5, color = 'k') 
plt.contourf(xi, yi, zi, 15, cmap=plt.cm.jet)
plt.quiver(x, z, u, w)
sm = plt.cm.ScalarMappable(cmap=colormap)
plt.colorbar(sm, label='Flux Density Magnitude [T]') # draw colorbar

plt.show()
# save file as PDF for high resolution