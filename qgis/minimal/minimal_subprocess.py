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
        self.btnE.pressed.connect(self.start_process)
        self.btnK = QPushButton("Kill")
        self.btnK.pressed.connect(self.kill_process)
        self.btnT = QPushButton("Terminate")
        self.btnT.pressed.connect(self.terminate_process)
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

    def kill_process(self):
        if self.p.poll() is not None:
            self.message('Kill')
            self.p.kill()

    def terminate_process(self):
        if self.p.poll() is not None:
            self.message('Terminate')
            self.p.terminate()

    def start_process(self):
        if self.p is None:  # No process running.
            self.message('Starting process')

            self.p = subprocess.Popen(['python3', 'dummy_proc.py'], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    cwd=self.plugin_dir)
            while True:
                out = self.p.stdout.readline()
                err = self.p.stderr.readline()
                if self.p.poll() is not None and out == b'' and err == b'':
                    break
                if out:
                    self.message('out %s'%out)
                if err:
                    self.message('err %s'%err)
            retval = self.p.poll()
            self.message('retval %s'%retval)

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
