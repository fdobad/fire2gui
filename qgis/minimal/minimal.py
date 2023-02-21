#!python3
import os.path
from qgis.core import (
    QgsApplication,
    QgsMessageLog,
    QgsTask,
    Qgis,
    )

from qgis.PyQt.QtCore import QTimer

from qgis.gui import (
    QgsMessageBar,
    )

from qgis.PyQt.QtWidgets import (
    QApplication,
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
from datetime import datetime
#from time import sleep
#from asyncio import sleep

aName = 'minimal plugin'
MESSAGE_CATEGORY = aName

class MyQgsTaks(QgsTask):
    def __init__(self, args, path, description):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.args = args
        self.description = description
        self.path = path if path is not None else os.path.dirname(os.path.abspath(__file__))
        self.proc = None

    def run(self):
        try:
            self.setProgress(0.0)
            QgsMessageLog.logMessage( 'Task {} run method started'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
            if self.proc is None:  # No process running.
                self.proc = subprocess.Popen(['python3','-u', 'dummy_timed_proc.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=None,
                        bufsize=0,
                        cwd=self.path)
                        #text=True,
                self.setProgress(10.0)
                nmax=500
                i=0
                while i<nmax:
                    output = self.proc.stdout.readline #(1) #line()
                    if self.proc.poll() is not None and not output:
                        break
                    if self.isCanceled():
                        QgsMessageLog.logMessage( 'isCanceled', MESSAGE_CATEGORY, Qgis.Info)
                        return False
                    if output:
                        QgsMessageLog.logMessage( 'stdout\t{}\t{}'.format(output.decode(), str(datetime.now())[-12:-4]), MESSAGE_CATEGORY, Qgis.Info)
                        self.setProgress(10+i/nmax*90)
                        QApplication.processEvents()
                        #sleep(1)
                        self.timer = QTimer()
                        self.timer.setSingleShot(True)
                        ##self.timer.timeout.connect(lambda: self.fupdate())
                        self.timer.start(500)
                    i+=1
                retval = self.proc.poll()
                self.proc.stdout.close()
                QgsMessageLog.logMessage( 'Task retval {} {}'.format(retval,i), MESSAGE_CATEGORY, Qgis.Info)
            self.proc = None
            self.setProgress(100.0)
            return True
        except Exception as e:
            self.exception = e
            return False

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed'.format(
                name=self.description),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without '\
                    'exception (probably the task was manually '\
                    'canceled by the user)'.format(
                    name=self.description),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage('Task "{name}" Exception: {exception}'.format(
                        name=self.description,
                        exception=self.exception),
                        MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        if self.proc is not None:
            self.proc.kill()
        super().cancel()
        QgsMessageLog.logMessage(
            'Task "{name}" cancel signal handled ok'.format(
            name=self.description),
            MESSAGE_CATEGORY, Qgis.Info)

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
        ''' QgsTask '''
        self.task = None
        self.taskManager = QgsApplication.taskManager()

    def message(self, s):
        self.text.appendPlainText(s)

    def kill(self):
        if self.task is not None:
            self.task.cancel()
            self.message('MyDlg killed task is %s'%self.task)

    def terminate(self):
        self.message('MyDlg NI terminated')

    def start(self):
        if self.task is None:  # No process running.
            self.message('MyDlg starting task %s'%self.task)
            self.task = MyQgsTaks('', path = self.plugin_dir, description = 'ledescr' )
            self.taskManager.addTask(self.task)

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
