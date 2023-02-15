#!/usr/bin/env python3
#REPLENV: /home/fdo/pyenv/qgis
from pandas import DataFrame, Series
import numpy as np

'''CONSTANTS'''
aName = 'fire2am'

from qgis.PyQt.QtWidgets import QGraphicsScene, QGraphicsProxyWidget, QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
class MatplotlibModel(QGraphicsScene):
    def __init__(self, parent=None):
        super(MatplotlibModel, self).__init__(parent)
        self.static_canvas = None
        self.static_ax = None

    def newStaticFigCanvas(self, w=4, h=6):
        self.static_canvas = FigureCanvas(Figure(figsize=(w, h)))
        self.static_ax = self.static_canvas.figure.subplots()
        return self.static_canvas, self.static_ax

    def setGraphicsView(self, gv):
        #scene = QGraphicsScene()
        proxy_widget = QGraphicsProxyWidget()
        widget = QWidget()
        layout = QVBoxLayout()
        #
        layout.addWidget(NavigationToolbar(self.static_canvas))
        layout.addWidget(self.static_canvas)
        #
        widget.setLayout(layout)
        proxy_widget.setWidget(widget)
        self.addItem(proxy_widget)
        gv.setScene(self)

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QVariant, QAbstractTableModel
class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(str(self._data.iloc[index.row(), index.column()]))
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

def randomNames(n=8, l=4):
    '''
    for i in range(20):
        for j in range(1,i):
           print(i,j,randomNames(i,j))
    '''
    m = n*l
    lis = map( chr, np.random.randint(97,123,size=m))
    joi = ''.join(lis)
    return [ joi[i:i+l] for i in range(0,m,l) ]

def randomDataFrame(rows=8, cols=4, dtype=float):
    if dtype == float:
        data = np.round( np.random.random(size=(rows,cols)) , 2)
    elif dtype == int:
        data =           np.random.randint(99, size=(rows,cols))
    else:
        raise NotImplementedError
    df = DataFrame( data, columns=randomNames(cols,3))
    df.insert( 0, randomNames(1,6)[0], Series(randomNames(rows,4)))
    return df

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def safe_cast_ok(val, to_type, default=None):
    try:
        return to_type(val), True
    except (ValueError, TypeError):
        return default, False

def check(obj,key):
    return hasattr(obj, key) and callable(getattr(obj, key))

def get_params(Parser):
    ''' get an argparse object that has groups '''
    parser, groups = get_grouped_parser(Parser())
    args = { dest:parser[dest]['default'] for dest in parser.keys() }
    return args, parser, groups

def get_grouped_parser(parser):
    '''see usr/lib/python39/argparse.py for details
        groups are stored on _action_groups, lines: 1352, 1448
    '''
    pag = parser.__dict__['_action_groups']
    '''
        p[0]['title'] : 'positional' 
        p[1]['title'] : 'optional arguments'
        p[2:]['title'] : groups
    '''
    q = {}
    for p in pag[2:]:
        r = p.__dict__
        q[r['title']] = r['_group_actions']
    groups = set(q.keys())
    # normalize 
    args = {}
    for k,v in q.items():
        for w in v:
            x = w.__dict__
            args[x['dest']] = x  
            args[x['dest']].pop( 'container')
            args[x['dest']].update({ 'group' : k})

    return args, groups

