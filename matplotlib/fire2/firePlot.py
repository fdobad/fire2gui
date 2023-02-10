#!python3
#REPLENV: /home/fdo/pyenv/dev
'''
For gifs: `sudo apt install imagemagick`

inspect Hom40x40 data:
for i in range(n):
   print( data[i] - data[j][5:14,1:9]/j for i in range(1,i))
'''
import glob, os
from time import sleep, time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use, get_backend
from matplotlib.animation import FuncAnimation
from matplotlib import colormaps, colors
from functools import partial
from imread import imread
use('QtAgg')
print(get_backend())

def get_data_Grids():
    gl=[]
    gd=[]
    for ffn in glob.glob('Grid*/*'):
        fn = os.path.basename(ffn)[:-4]
        gl += [fn]
        gd += [np.genfromtxt(ffn, delimiter=",", dtype=np.int16)]
    n=len(gl)
    gl = np.array(gl)
    gd = np.array(gd)
    ind = np.argsort(gl)
    gl = gl[ind]
    gd = gd[ind]
    W, H = np.int32( gd[0].shape)
    return gd, W, H, n, gl
#data, W, H, n, names = get_data_Grids()

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
#register_colormap_inferno0()

def build(  window_title='window_title_is_fignum',
            figure_suptitle='figure_title',
            ax_title='ax_title', 
            xlabel='W - E', 
            ylabel='N - S',
            *args, **kwargs):
    plt.close('all')
    px = 1/plt.rcParams['figure.dpi']
    Wpx, Hpx = 600*px, 600*px
    fig, ax = plt.subplots( figsize=(Wpx, Hpx),
            num=window_title,
            subplot_kw=dict(aspect="equal"))
    fig.suptitle( figure_suptitle)
    ax.set( xlabel=xlabel, ylabel=ylabel, title=ax_title)
    return fig, ax
#fix, ax = build()
#ax.plot([1,2],[3,4])
#plt.show()

def pltQuadMesh():
    i=5
    fig, ax = build(figure_suptitle='pltQuadMesh', ax_title='Fire scar data[%s]'%i)
    assert len(data[i][data[i]!=0])
    plt.pcolormesh( data[i], figure=fig, cmap='inferno0', vmin=0, vmax=1)
    plt.show()

def pltFuncAnimation():
    fig, ax = build(figure_suptitle='pltFuncAnimation', ax_title='forest fire evolution step  ')
    x = np.arange(W)
    y = np.arange(H)
    b = np.empty((W,H),dtype=np.int16)
    plt.pcolormesh(x,y,b, cmap='inferno0', vmin=0, vmax=1 )
    def animate( i):
        plt.title('forest fire evolution step %s'%i)
        if i==0:
            plt.pcolormesh(x,y, data[i])
            return
        plt.pcolormesh(x,y, data[i]-data[i-1]/2, cmap='inferno0', vmin=0, vmax=1)
    anime = FuncAnimation(fig, animate, frames = range(n), blit = False)
    plt.show()
#pltFuncAnimation()

def build_background(image_file='background.png',*args, **kwargs):
    fig, ax = build(*args, **kwargs)
    if 'W' in kwargs.keys():
        W=kwargs['W']
    if 'H' in kwargs.keys():
        H=kwargs['W']
    img = imread(image_file)
    #fig.figimage(img) fill full figure not axes
    ax.imshow(img, extent=[-0.5, W, -0.5, H] )#, zorder=-1.0) not needed if plot in order
    # extent -0.5 by pcolormesh centers cells on integers
    return fig, ax
#build_background()
#plt.show()

def qmAnimation():
    #fig, ax = build()
    fig, ax = build_background(W=W,H=H,figure_suptitle='qmAnimation')
    x = np.arange(W)
    y = np.arange(H)
    # v0
    #z0 = np.zeros((W,H),dtype=np.int16)
    #qm = plt.pcolormesh(x,y,z0, cmap='inferno0', vmin=0, vmax=1 ,animated=True)
    # v1
    # send zeros where the fire will happen
    # don't build artists where not needed
    z1 = np.ones((W,H),dtype=np.int16)
    mask = np.ma.masked_equal( 1-data[-1], z1)
    qm = plt.pcolormesh(x,y,mask, cmap='inferno0', vmin=0, vmax=1 , zorder=1.0)
    #
    xlabel,ylabel,title = ax.set(xlabel='W - E', ylabel='S - N', title='forest fire evolution step ')
    #
    def animate( i):
        title.set_text('forest fire evolution step %s'%i)
        #qm.set_array(data[i])
        # old fires get darker
        qm.set_array(data[i] - sum(data[j]/n for j in range(i)))
        return qm, title,
    anime = FuncAnimation(fig, animate, frames = range(n), blit = False)
    plt.show()
    plt.rcParams['animation.convert_path'] = r'/usr/bin/convert'
    anime.save('fireEvolution.gif', writer='imagemagick', fps=3)
#qmAnimation()

def qmBlitAnimation():
    fig, ax = build_background(W=W,H=H,figure_suptitle='qmBlitAnimation')
    x = np.arange(W)
    y = np.arange(H)
    # send zeros where the fire will happen
    # don't build artists where not needed
    z1 = np.ones((W,H),dtype=np.int16)
    mask = np.ma.masked_equal( 1-data[-1], z1)
    qm = plt.pcolormesh(x,y,mask, cmap='inferno0', vmin=0, vmax=1, animated=True, zorder=1.0)
    #
    xlabel,ylabel,title = ax.set(xlabel='W - E', ylabel='S - N', title=' ')
    #
    title_ann = ax.annotate(
            "forest fire evolution step",
            (0.5, 1),
            xycoords="axes fraction",
            xytext=(10, 10),
            textcoords="offset points",
            ha="center",
            va="top",
            animated=True,
    )
    def animate( i):
        title_ann.set_text( 'forest fire evolution step %s'%i)
        qm.set_array(data[i] - sum(data[j]/n for j in range(i)))
        return qm, title_ann,
    anime = FuncAnimation(fig, animate, frames = range(n), blit = True)
    plt.show()
    plt.rcParams['animation.convert_path'] = r'/usr/bin/convert'
    anime.save('fireEvolution.gif', writer='imagemagick', fps=3)
#qmBlitAnimation()

def main():
    global data, W, H, n, names
    data, W, H, n, names = get_data_Grids()

    register_colormap_inferno0()

    pltQuadMesh()
    pltFuncAnimation()
    
    qmAnimation()
    qmBlitAnimation()
    
if __name__ == '__main__':
    main()

'''
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
