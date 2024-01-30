import matplotlib.pyplot as plt
import numpy as np

ax = plt.figure().add_subplot(projection='3d')

# read data from file

def getfiledata(a):
    initial = a.readline().strip().split(', ')
    return [float(i) for i in initial]

def read_(f):
    u = getfiledata(f)
    v = getfiledata(f)
    w = getfiledata(f)
    x = getfiledata(f)
    y = getfiledata(f)
    z = getfiledata(f)
    strengths = []
    for i in range(len(u)):
        a = u[i]
        b = v[i]
        c = w[i]
        size = np.sqrt(a**2+b**2+c**2)
        u[i] = a/size
        v[i] = b/size
        w[i] = c/size
        strengths.append(size)
    print("Max strength:", np.max(strengths))

a = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\mc_n52_1_data_S.txt','r')
b = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\mc_n52_2_data_S.txt','r')
c = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\mc_n52_3_data_S.txt','r')
d = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\n52_1_data_S.txt','r')
e = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\n52_2_data_S.txt','r')
f = open(r'c:\Users\samar\OneDrive\Documents\Magnetometer data\n52_data\n52_3_data_S.txt','r')

for i in ([a,b,c,d,e,f]):
    read_(i)


# # create colormap
# color_strengths = []
# for i in range(len(u)):
#     a = u[i]
#     b = v[i]
#     c = w[i]
#     size = np.sqrt(a**2+b**2+c**2)
#     u[i] = a/size
#     v[i] = b/size
#     w[i] = c/size
#     color_strengths.append(size)

# color_scalars = []
# a = np.min(color_strengths)
# b = np.max(color_strengths)
# print("Max field strength:", b)
# for i in color_strengths:
#     color_scalars.append((i - a) / (b-a))

# ncs = color_scalars.copy()
# for i in color_scalars:
#     ncs.append(i)
#     ncs.append(i)

# # make alpha a little higher so it's not too transparent
# transparencies = ncs.copy()
# for i in range(len(transparencies)):
#     val = transparencies[i]
#     transparencies[i] = val + 0.25
#     if transparencies[i] > 1:
#         transparencies[i] = 1

# # print(color_strengths)
# # print(color_scalars)

# cmap = plt.get_cmap('plasma')
# vnew = [-i for i in v]
# ax.quiver(x, y, z, u, w, vnew, color=cmap(ncs), pivot='middle', length=0.5, alpha=transparencies)
# maxrange = max(max(x),max(y),max(z))
# ax.set_xlim(0,maxrange)
# ax.set_ylim(0,maxrange)
# ax.set_zlim(0,maxrange)

# plt.show()
# # save file as PDF for high resolution

