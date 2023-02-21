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

from qgis.PyQt.QtCore import QProcess

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
        if self.p and self.p.state()!=0:
            self.message('Kill')
            self.p.kill()

    def terminate_process(self):
        if self.p and self.p.state()!=0:
            self.message('Terminate')
            self.p.terminate()

    def start_process(self):
        if self.p is None:  # No process running.
            self.message('Starting process')
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.

            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            #self.p.setProcessChannelMode(QProcess.MergedChannels)
            #self.p.setProcessChannelMode(QProcess.ForwardedOutputChannel)
            #self.p.setProcessChannelMode(QProcess.ForwardedErrorChannel)
            self.p.setProcessChannelMode(QProcess.SeparateChannels)

            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            #1
            self.p.setWorkingDirectory(self.plugin_dir)
            self.p.start('python3', ['dummy_proc.py'])
            #2
            #self.p.setWorkingDirectory('/home/fdo/source/C2FSBd')
            #self.p.start('python3','main.py --input-instance-folder data/Hom_Fuel_101_40x40/ --output-folder out --verbose'.split())
            #3
            #self.p.setWorkingDirectory(self.plugin_dir)
            #self.p.start('python3', 'wrapper.py /home/fdo/source/C2FSBd main.py --input-instance-folder data/Hom_Fuel_101_40x40/ --output-folder out --verbose --stats --allPlots --grids --output-messages'split())

    def handle_stderr(self):
        self.message('handle_stderr')
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        QgsMessageLog.logMessage('handle_stderr %s'%stderr, aName, level=Qgis.Info)
        self.message(stderr)

    def handle_stdout(self):
        self.message('handle_stdout')
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        QgsMessageLog.logMessage('handle_stdout %s'%stdout, aName, level=Qgis.Info)
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None

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
