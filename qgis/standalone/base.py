#REPLENV: /home/fdo/pyenv/dev/bin/activate
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys

app = QApplication(sys.argv)
widget = QWidget()
layout = QVBoxLayout()
from PyQt5.QtWidgets import QComboBox

com = QComboBox()
