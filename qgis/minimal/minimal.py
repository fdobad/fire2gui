#!python3
from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsGeometry,
    )

from qgis.gui import (
    QgsMessageBar,
    )

from qgis.PyQt.QtWidgets import (
    QAction, 
    QMessageBox,
    QDialog, 
    QDialogButtonBox,
    QGridLayout, 
    QSizePolicy,
    )

class MyDialog(QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
    #def __init__(self):
    #    QDialog.__init__(self)
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttonbox.accepted.connect(self.run)
        self.buttonbox.clicked.connect(self.run2)
        self.layout().addWidget(self.buttonbox, 0, 0, 2, 1)
        self.layout().addWidget(self.bar, 0, 0, 1, 1)
        self.run()
    def run(self):
        self.bar.pushMessage("Hello", "World", level=Qgis.Info, duration=3)
    def run2(self):
        self.bar.pushMessage("Bye", "World", level=Qgis.Info, duration=3)

class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('Go!', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        #QgsMessageLog.logMessage("(minimal.run) Hello World!", 'FirePlugin', level=Qgis.Info)
        myDlg = MyDialog(parent=self.iface.mainWindow())
        myDlg.show()
        #myDlg.run()
        #QMessageBox.information(None, 'Minimal plugin', 'Do something useful here')
        #QgsMessageLog.logMessage("(minimal.run) Bye World!", 'FirePlugin', level=Qgis.Info)
