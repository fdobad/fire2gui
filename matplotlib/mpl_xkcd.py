import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib import use, get_backend
from matplotlib.patches import Rectangle
use('QtAgg')
print(get_backend())
'''
Not useful:
    api to access comics not fonts https://packages.debian.org/bullseye/python3-xkcd
    https://xkcd.com/797/

Install fonts
    git clone git@github.com:ipython/xkcd-font.git
    2dary button over .ttf > open with fonts > install
    else:
        install fontManager (done visually in gnome)
        in fontManager gui add fonts
    gets installed in: .local/share/fonts/Unknown Vendor/TrueType/xkcd Script/xkcd_Script_Regular.ttf

BUT
MPL fontManager floods with warning about incomplete fonts:
    disable loggin for that module


plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Tahoma']


fpath = Path(mpl.get_data_path(), "fonts/ttf/cmr10.ttf")
ax.set_title(f'This is a special font: {fpath.name}', font=fpath)
ax.set_xlabel('This is the default font')
'''
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

px = 1/plt.rcParams['figure.dpi']

def main():
    piramidChart()
    #pieChart()
    #singleWave()
    #Animate()

def setFont():
    font_path = '/System/Library/Fonts/PingFang.ttc'  # the location of the font file
    my_font = fm.FontProperties(fname=font_path)

def cleanRebuildmplFonts():
    import shutil
    import matplotlib
    shutil.rmtree(matplotlib.get_cachedir())
    fm = matplotlib.font_manager.FontManager()
    fm.findfont('xkcd_script')
    #fm.findfont('xkcd-script')

def Animate():
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from functools import partial
    
    fig, ax = plt.subplots()
    line1, = ax.plot([], [])
    #line1, = ax.plot([], [], 'ro')
    def init():
        ax.set(xlabel='time (s)', ylabel='voltage (mV)',
               title='About as simple as it gets, folks')
        #ax.set_xlim(0, 2*np.pi)
        ax.set_ylim(-1, 1)
        return line1,
    
    def update(frame, ln, x, y):
        t = np.linspace(0, 10, 101)
        x.append(t)
        y.append(np.sin(t+frame))
        ln.set_data(x, y)
        return ln,
    
    ani = FuncAnimation(
        fig, partial(update, ln=line1, x=[], y=[]),
        #frames=np.linspace(0, 2*np.pi, 128),
        frames=np.arange(200),
        init_func=init, blit=True)
    
    plt.show()

def update_canvas(line):
    t = np.linspace(0, 10, 101)
    # Shift the sinusoid as a function of time.
    line.set_data(t, np.sin(t + time.time()))
    line.figure.canvas.draw()
    #line.figure.canvas.draw_idle()

def singleWave():
    global timer
    with plt.xkcd(scale=10, length=250, randomness=9):
        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (mV)',
               title='About as simple as it gets, folks')
        t = np.linspace(0, 10, 101)
        line, = ax.plot(t, np.sin(t + time.time()))
        timer = fig.canvas.new_timer(interval=100)
        timer.add_callback(update_canvas, line)
        timer.start()
        plt.show()

def pieChart():
    with plt.xkcd(scale=2, length=150, randomness=3):
        fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
        
        recipe = ["375 g flour",
                  "75 g sugar",
                  "250 g butter",
                  "300 g berries"]
        
        data = [float(x.split()[0]) for x in recipe]
        ingredients = [x.split()[-1] for x in recipe]
        
        
        def func(pct, allvals):
            absolute = int(np.round(pct/100.*np.sum(allvals)))
            return "{:.1f}%\n({:d} g)".format(pct, absolute)
        
        
        wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data),
                                          textprops=dict(color="w"))
        
        ax.legend(wedges, ingredients,
                  title="Ingredients",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.setp(autotexts, size=8, weight="bold")
        
        ax.set_title("Matplotlib bakery: A pie")
        
        plt.show()

def piramidChart():
    px = 1/plt.rcParams['figure.dpi']
    with plt.xkcd(scale=2, length=150, randomness=3):
        W, H = 400*px, 600*px
        fig, ax = plt.subplots(num=1, figsize=(W, H), subplot_kw=dict(aspect="equal"))
        #fig.set_edgecolor((0,0,0,0))
        labels = ["sky", "pyramid", "shaded pyramid"]
        data = [265, 80, 15]
        colors = [ (57,84,91,100), (91,62,41,100), (46,36,34,100)]
        colors = np.array(colors)/100
        rec = Rectangle((0.02,0.02),0.96,0.96, alpha=1, facecolor='none', edgecolor='black',zorder=0, clip_on=False)
        rec.set_transform(ax.transFigure)
        ax.add_patch(rec)
        wedges, texts = ax.pie(data, colors=colors, startangle=220, counterclock=False, shadow=False, labels=labels, labeldistance=None)
        ax.set_title("Newest DataScience Breakthrough:", y=1.1)
        legend = ax.legend(loc=(0.15,-0.33))
        legend.set_transform(fig.transFigure)
        plt.show()

if __name__ == '__main__':
    main()
