#REPLENV: /home/fdo/pyenv/qgis
import sys
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt import QtWidgets
Qt = QtCore.Qt
from pandas import DataFrame
import numpy as np

def randomDataFrame():
    r,c = 4,6
    data = np.random.random(size=(r,c))
    columns = map(chr,np.random.randint(97,123,size=c))
    return DataFrame( data , columns=columns)


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.values[index.row()][index.column()]))
        return QtCore.QVariant()


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    view = QtWidgets.QTableView()
    model = PandasModel(randomDataFrame())
    view.setModel(model)

    view.show()
    sys.exit(application.exec_())
