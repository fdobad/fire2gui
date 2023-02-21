from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout
from qgis.PyQt.QtCore import QTimer

class MyDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.parent = parent
        self.setLayout(QVBoxLayout())
        self.timer = QTimer
        self.val = 0
        print('init')

    def nocancel(self ):
        self.timer.disconnect()
        print('nocancel')

    def nofunc(self ):
        self.val += 1
        print('nofunc', self.val)

    def nostart(self, tpo=1000):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.nofunc)
        self.timer.start(tpo)
        print('nostart')

if __name__ == '__main__':
    print('hello')
    QgsApplication.setPrefixPath('/application/path/to/adapt', True)
    app = QgsApplication([], True)
    app.initQgis()
    dialog = MyDialog(app)
    dialog.nostart()
    app.exitQgis()
