#REPLENV: /home/fdo/pyenv/dev
#!python3
import glob, os
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use, get_backend
from matplotlib.animation import FuncAnimation
from functools import partial
use('QtAgg')
print(get_backend())

def data():
    gl=[]
    gd=[]
    for ffn in glob.glob('Grid*/*'):
        fn = os.path.basename(ffn)[:-4]
        gl += [fn]
        gd += [np.genfromtxt(ffn, delimiter=",")]
    n=len(gl)
    gl = np.array(gl)
    gd = np.array(gd)
    ind = np.argsort(gl)
    gl = gl[ind]
    gd = gd[ind]
    W, H = np.int32( gd[0].shape)
    return gd, W, H, n, gl
data, W, H, n, names = data()
print(W, H, n, names)

'''
for i in range(n):
   print( data[i] - data[j][5:14,1:9]/j for i in range(1,i))
   '''

from matplotlib import colormaps, colors
def register_colormap_inferno0():
    '''https://matplotlib.org/stable/tutorials/colors/colormap-manipulation.html
    '''
    cm = colormaps['inferno']
    cl = np.array( cm.colors )
    cla = np.empty( (256,4) , dtype=cl.dtype)
    cla[:,:3] = cl
    cla[:,3] = 1
    cla[0,3] = 0
    my_cmap = colors.LinearSegmentedColormap.from_list("inferno0",cla)
    colormaps.register(cmap=my_cmap)
register_colormap_inferno0()

def build():
    plt.close('all')
    px = 1/plt.rcParams['figure.dpi']
    Wpx, Hpx = 600*px, 600*px
    fig, ax = plt.subplots(num=1, figsize=(Wpx, Hpx), subplot_kw=dict(aspect="equal"))
    ax.set(xlabel='W - E', ylabel='N - S', title='ff evo')
    return fig, ax
fig, ax = build()

def singleFrame():
    fig, ax = build()
    i=3
    assert len(data[i][data[i]!=0])
    ax.set_title('ff %s'%i)
    qm = ax.pcolormesh( data[i], figure=fig, cmap=plt.cm.inferno, vmin=0, vmax=1)
    plt.show(block=False)

from imread import imread
def background():
    fig, ax = build()
    img = imread('background.png')
    #fig.figimage(img) fill full figure not axes
    plt.imshow(img, extent=[0, W, 0, H], zorder=0.0)
    return fig, ax
fig, ax = background()

def qmAnimation():
    ''' TODO : blit and iterate over the list of artists defined by the fire (data!=0)
    blit=True is looking for a list of objects to update. If you assign a handle to your pcolormesh object, e.g. pcm = plt.pcolormesh(X[0:1], Y[0:1], C[0:1]) then you can update the pcm's data with pcm.set_array(new_cdata)
    '''
    x = np.arange(W)
    y = np.arange(H)
    z = np.ones((W,H),dtype=np.int16)
    qm = plt.pcolormesh(x,y,z, cmap='inferno0', vmin=0, vmax=1 , zorder=1.0)
    xlabel,ylabel,title = ax.set(xlabel='W - E', ylabel='S - N', title='forest fire evolution step ')

    def animate( i):
        title.set_text('forest fire evolution step %s'%i)
        qm.set_array(data[i] - sum(data[j]/n for j in range(i)))
        #qm.set_array(data[i])
        return qm

    anime = FuncAnimation(fig, animate, frames = range(n), blit = False)
    plt.show()
    plt.rcParams['animation.convert_path'] = r'/usr/bin/convert'
    anime.save('fireEvolution.gif', writer='imagemagick', fps=3)
qmAnimation()

def pltAnimation():
    fig, ax = build()
    x = np.arange(W)
    y = np.arange(H)
    b = np.empty((W,H),dtype=np.int16)
    plt.pcolormesh(x,y,b, cmap=plt.cm.inferno, vmin=0, vmax=1 )
    ax.set(xlabel='W - E', ylabel='N - S', title='ff evo')

    def animate( i):
        plt.title('PLT forest fire evolution step %s'%i)
        if i==0:
            plt.pcolormesh(x,y, data[i])
            return
        plt.pcolormesh(x,y, data[i]-data[i-1]/2, cmap=plt.cm.inferno, vmin=0, vmax=1)
    
    anime = FuncAnimation(fig, animate, frames = range(n), blit = False)
    
    plt.show()
#pltAnimation()

'''
plt.hold(True)
plt.pcolormesh(np.zeros((W,H)))
anim = animation.FuncAnimation(fig, animate, frames = range(n), blit = False)
plt.show()
plt.hold(False)

def animate( self, i):
    plt.title('ff %s, non-zero:%s'%(i,len(data[i][data[i]!=0])))
    plt.pcolormesh(data[i])

plt.show(block=False)
for i,dat in enumerate(data):
    print('ff %s'%i)
    ax.set_title('ff %s, non-zero:%s'%(i,len(data[i][data[i]!=0])))
    qm = ax.pcolormesh( data[i], figure=fig, cmap=plt.cm.inferno, vmin=0, vmax=1) #.set(animated=True)
    fig.canvas.draw()
    plt.show(block=False)
    sleep(0.5)

plt.close('all')

qm = ax.pcolormesh( data[3], cmap=plt.cm.inferno, vmin=0, vmax=1)

qm = ax.pcolormesh( np.zeros( ( W, H), dtype=np.int32), cmap=plt.cm.inferno, data=frames)
qm = ax.pcolormesh( frames, animated=True, figure=fig, cmap=plt.cm.inferno, data=frames)
plt.show(block=False)

ax.set(xlabel='W - E', ylabel='S - N', title='Fire evolution')


#axi = ax.pcolor( np.zeros( ( W, H), dtype=np.int32), cmap = plt.cm.inferno)

plt.show(block=False)
axi.set_data(frames[1])

col = ax.pcolor( frames[0], cmap = plt.cm.inferno)
plt.show()
col = ax.pcolor( frames[1], cmap = plt.cm.inferno)
plt.show()
col = ax.pcolor( frames[2], cmap = plt.cm.inferno)
plt.show()
col = ax.pcolor( frames[3], cmap = plt.cm.inferno)
plt.show()
col = ax.pcolor( frames[4], cmap = plt.cm.inferno)
plt.show()
col = ax.pcolor( frames[5], cmap = plt.cm.inferno)
plt.show()

def init():
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    return ax,

def update(frame, ax):
    print(frame.shape, ax)
    axi = ax.matshow( frame, cm = plt.cm.inferno)
    #ax.set_data(frame)
    return ax,

ani = FuncAnimation(
    fig, partial(update, ax=ax),
    frames=frames,
    init_func=init, blit=True)

plt.show()
'''
