import sys
from PyQt5 import QtCore, QtWidgets

class Example(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Example, self).__init__(parent)

        self.app_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.app_layout)

        self.setGeometry(300, 300, 50, 50)

        self.count_to = 10
        self.delay = 5000

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)

        # start button
        start_button = QtWidgets.QPushButton()
        start_button.setText('START')
        start_button.clicked.connect(self.startCount)
        self.app_layout.addWidget(start_button)

        # number button
        self.number_button = QtWidgets.QPushButton()
        self.number_button.setText('0')
        self.app_layout.addWidget(self.number_button)

    def startCount(self):
        def updateButtonCount():
            self.number_button.setText("%s" % count)

        for count in range(0, self.count_to):
            self.timer.singleShot(self.delay, updateButtonCount)

def main():
    app = QtWidgets.QApplication(sys.argv)
    example = Example()
    example.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
