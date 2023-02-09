#REPLENV: /home/fdo/pyenv/qgis
import numpy as np
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import use, get_backend
use('QtAgg')
print(get_backend())
import matplotlib.pyplot as plt
import numpy as np
import time

def basicTest():
    # Data for plotting
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)
    fig, ax = plt.subplots()
    ax.plot(t, s)
    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='About as simple as it gets, folks')
    ax.grid()
    fig.savefig("test.png")
    plt.show()

def addStaticCanvas(layout):
    static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    static_ax = static_canvas.figure.subplots()
    static_ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Static -- About as simple as it gets, folks')
    t = np.linspace(0, 10, 50)
    static_ax.plot(t, np.tan(t), ".")
    layout.addWidget(NavigationToolbar(static_canvas))
    layout.addWidget(static_canvas)

def update_canvas(line):
    t = np.linspace(0, 10, 101)
    # Shift the sinusoid as a function of time.
    line.set_data(t, np.sin(t + time.time()))
    line.figure.canvas.draw()
    #line.figure.canvas.draw_idle()

def start_timer(event):
    global timer, dynamic_canvas, drawid
    timer.start()
    dynamic_canvas.mpl_disconnect(drawid)

def addDynamicCanvas(layout, v : int = 1):
    if v == 1:
        global timer
    if v == 2:
        global timer, dynamic_canvas, drawid
    dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    layout.addWidget(NavigationToolbar(dynamic_canvas))
    layout.addWidget(dynamic_canvas)
    dynamic_ax = dynamic_canvas.figure.subplots()
    dynamic_ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Dynamic Canvas v%s -- About as simple as it gets, folks'%v)
    t = np.linspace(0, 10, 101)
    # Set up a Line2D.
    line, = dynamic_ax.plot(t, np.sin(t + time.time()))
    timer = dynamic_canvas.new_timer(interval=100)
    timer.add_callback(update_canvas, line)
    #cb_id = timer.add_callback(update_canvas, line)
    if v == 1:
        timer.start()
    if v == 2:
        drawid = dynamic_canvas.mpl_connect('draw_event', start_timer)


def buildWidgetApp():
    # Check whether there is already a running QApplication (e.g., if running from an IDE).
    app = QApplication.instance()
    if not app:
        print('not app')
        app = QApplication(sys.argv)

    widget = QWidget()
    scene = QGraphicsScene()
    view = QGraphicsView()
    layout = QVBoxLayout()
    widget.setLayout(layout)
    return app, widget, scene, view, layout

def showApp( app, widget, show = 'widget'):
    if show == 'widget':
        widget.show()
    elif show == 'window':
        window = QMainWindow()
        window.setCentralWidget(widget)
        window.setWindowTitle('qt matplotlib poc')
        window.show()
    else:
        print('show what?')
        raise SyntaxError 
    #sys.exit(app.exec_())
    app.exec_()

def main():
    #print('doin basic pyplot interactive test')
    #basicTest()

    #app, widget, scene, view, layout = buildWidgetApp()
    #addStaticCanvas(layout)
    #showApp(app, widget)

    #del app, widget, scene, view, layout 
    app, widget, scene, view, layout = buildWidgetApp()
    addDynamicCanvas(layout, v=1)
    showApp(app, widget)

    del app, widget, scene, view, layout 
    app, widget, scene, view, layout = buildWidgetApp()
    addDynamicCanvas(layout, v=2)
    showApp(app, widget)

if __name__ == '__main__':
    main()

'''
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot([1, 2, 3, 4], [0, 0.5, 1, 0.2])

    canvas = FigureCanvas(figure)
    proxy_widget = scene.addWidget(canvas)
    # or
    # proxy_widget = QtWidgets.QGraphicsProxyWidget()
    # proxy_widget.setWidget(canvas)
    # scene.addItem(proxy_widget)

    FigureCanvas.__init__(self, fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

    class Main_Code:
        def __init__(self):
            self.app = QtWidgets.QApplication(sys.argv)
            self.MainWindow = QtWidgets.QMainWindow()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self.MainWindow)
            self.MainWindow.showMaximized()
            self.init_ui()
            sys.exit(self.app.exec_())
        def init_ui(self):
            self.ui.graphicsView.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            self.MainWindow.setStyleSheet("background-color: black;")
            self.ui.graphicsView.setStyleSheet("background-color: yellow;")
            self.scene = QtWidgets.QGraphicsScene()
            self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.red))
            self.ui.graphicsView.setScene(self.scene)
            QtCore.QTimer.singleShot(100, self.draw_line)
        def draw_line(self):
            r = self.ui.graphicsView.mapToScene(
                self.ui.graphicsView.viewport().rect()
            ).boundingRect()
            self.timeline_line_top = QtWidgets.QGraphicsLineItem(
                QtCore.QLineF(r.bottomLeft(), r.topRight())
            )
            self.scene.addItem(self.timeline_line_top)
'''

