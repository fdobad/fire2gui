#!python3
#REPLENV: /home/fdo/pyenv/qgis
from pandas import DataFrame, Series
import numpy as np

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
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(str(
                    self._data.values[index.row()][index.column()]))
        return QVariant()

'''
qabstractitemview.SelectionMode ENUMS:
    ContiguousSelection
    ExtendedSelection
 2->MultiSelection
    NoSelection
    SingleSelection
class PieView : public QAbstractItemView
{
    void setSelection(const QRect&, QItemSelectionModel::SelectionFlags command) override;
'''

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
    columns = map( chr, np.random.randint(97,123,size=cols))
    df = DataFrame( data, columns=columns)
    df.insert( 0, randomNames(1,4)[0], Series(randomNames(rows,4)))
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


