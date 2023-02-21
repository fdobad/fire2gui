#!python3
import os.path
from qgis.core import (
    Qgis,
    QgsMessageLog,
    )

from qgis.gui import (
    QgsMessageBar,
    )

from qgis.PyQt.QtWidgets import (
    QAction, 
    QVBoxLayout, 
    QSizePolicy,
    QMessageBox,
    QDialog, 
    #QDialogButtonBox,
    QPushButton,
    QPlainTextEdit,
    )

import subprocess

aName = 'minimal plugin'

class MyDialog(QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.plugin_dir = os.path.dirname(__file__)
        ''' ui '''
        self.setWindowTitle('Minimal Plugin Dialog')
        self.btnE = QPushButton("Execute")
        self.btnE.pressed.connect(self.start)
        self.btnK = QPushButton("Kill")
        self.btnK.pressed.connect(self.kill)
        self.btnT = QPushButton("Terminate")
        self.btnT.pressed.connect(self.terminate)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.btnE)
        self.layout().addWidget(self.text)
        self.layout().addWidget(self.btnK)
        self.layout().addWidget(self.btnT)
        self.layout().addWidget(self.bar)
        ''' proc '''
        self.p = None

    def message(self, s):
        self.text.appendPlainText(s)

    def kill(self):
        if self.p is not None:
            self.p += self.p 
            self.message('killed p is %s'%self.p)

    def terminate(self):
        if self.p is not None:
            self.p = None
            self.message('terminated')

    def start(self):
        if self.p is None:  # No process running.
            self.p = 1
            self.message('Starting p is %s'%self.p)

class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.first_start = None

    def initGui(self):
        self.action = QAction('Go!', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.first_start = True

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dialog = MyDialog(parent=self.iface.mainWindow())
            self.dialog.bar.pushInfo('first started', aName)
            QgsMessageLog.logMessage('first started', aName, level=Qgis.Info)
        self.dialog.show()
        result = self.dialog.exec_()
        if result:
            QgsMessageLog.logMessage('result True', aName, level=Qgis.Info)
        QgsMessageLog.logMessage('result False', aName, level=Qgis.Info)
