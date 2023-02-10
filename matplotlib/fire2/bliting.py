#!python3
from time import sleep, time
import numpy as np
import matplotlib.pyplot as plt
from firePlot import get_data_Grids, build_background, build, register_colormap_inferno0

class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for subclasses of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
        cv.flush_events()

def blit2():
    data, W, H, n, names = get_data_Grids()
    register_colormap_inferno0()
    #fig, ax = build(figure_suptitle='blit2',ax_title=' ')
    fig, ax = build_background(W=W,H=H,figure_suptitle='blit2',ax_title=' ')

    x = np.arange(W)
    y = np.arange(H)
    # send zeros where the fire will happen
    # don't build artists where not needed
    z1 = np.ones((W,H),dtype=np.int16)
    mask = np.ma.masked_equal( 1-data[-1], z1)
    qm = plt.pcolormesh(x,y,mask, cmap='inferno0', vmin=0, vmax=1 , zorder=1.0, animated=True)
    xlabel,ylabel = ax.set(xlabel='W - E', ylabel='S - N')
    #
    fps_ann = ax.annotate(
            "fps: 0",
            (0, 1),
            xycoords="axes fraction",
            xytext=(10, 10),
            textcoords="offset points",
            ha="left",
            va="top",
            animated=True,
    )
    title_ann = ax.annotate(
            "forest fire evolution step ",
            (0.5, 1),
            xycoords="axes fraction",
            xytext=(10, 10),
            textcoords="offset points",
            ha="center",
            va="top",
            animated=True,
    )
    #
    bm = BlitManager(fig.canvas, [qm, fps_ann, title_ann])
    # make sure our window is on the screen and drawn
    plt.show(block=False)
    plt.pause(.1)
    #
    t = time()
    for j in range(1000):
        i=j%n
        # update the artists
        qm.set_array( data[i] - sum(data[j]/n for j in range(i)))
        title_ann.set_text( 'forest fire evolution step %s'%i)
        fps_ann.set_text( 'fps: %1.2f'%(1/(time()-t)))
        # tell the blitting manager to do its thing
        bm.update()
        t = time()

def blit1():
    x = np.linspace(0, 2 * np.pi, 100)
    # make a new figure
    fig, ax = plt.subplots()
    # add a line
    (ln,) = ax.plot(x, np.sin(x), animated=True)
    # add a frame number
    fr_number = ax.annotate(
        "0",
        (0, 1),
        xycoords="axes fraction",
        xytext=(10, -10),
        textcoords="offset points",
        ha="left",
        va="top",
        animated=True,
    )
    bm = BlitManager(fig.canvas, [ln, fr_number])
    # make sure our window is on the screen and drawn
    plt.show(block=False)
    plt.pause(.1)
    
    for j in range(100):
        # update the artists
        ln.set_ydata(np.sin(x + (j / 100) * np.pi))
        fr_number.set_text(f"frame: {j}")
        # tell the blitting manager to do its thing
        bm.update()

def main():
    plt.close('all')
    #blit1()
    blit2()
    
if __name__ == '__main__':
    main()
