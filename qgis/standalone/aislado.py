
#from PyQt6.QtWidgets import QApplication, QWidget
from qgis.PyQt.QtWidgets import QDialog, QApplication, QWidget

# create the QApplication
app = QApplication([])

# create the main window
window = QWidget(windowTitle='Hello World')

window.setWindowTitle('hola')

window.show()

# start the event loop
app.exec()

#from qgis.PyQt.QtWidgets import QDialog, QApplication
#from qgis.gui import QgsFileWidget
#
#app = QApplication([])
#new_dialog = QDialog()
#new_dialog.resize(400, 300)
#file_widget = QgsFileWidget(new_dialog)
#
#new_dialog.show()
