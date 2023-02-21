from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QProcess
import sys

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.p = None

        self.btnE = QPushButton("Execute")
        self.btnE.pressed.connect(self.start_process)
        self.btnK = QPushButton("Kill")
        self.btnK.pressed.connect(self.kill_process)
        self.btnT = QPushButton("Terminate")
        self.btnT.pressed.connect(self.terminate_process)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        l = QVBoxLayout()
        l.addWidget(self.btnE)
        l.addWidget(self.text)
        l.addWidget(self.btnK)
        l.addWidget(self.btnT)

        w = QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)

    def message(self, s):
        self.text.appendPlainText(s)

    def kill_process(self):
        if self.p and self.p.state()!=0:
            self.p.kill()

    def terminate_process(self):
        if self.p and self.p.state()!=0:
            self.p.terminate()

    def start_process(self):
        if self.p is None:  # No process running.
            self.message("Executing process")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.setInputChannelMode(QProcess.ForwardedInputChannel)
            self.p.setProcessChannelMode( QProcess.SeparateChannels)
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            #self.p.setWorkingDirectory()
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start("python3", ['dummy_proc.py'])

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message('e '+stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message('o '+stdout)
        #data = self.p.readLine()
        #msg = 'sender %s %s' % ( self.sender(),dir(self.sender()))
        #self.message(msg)

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


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
