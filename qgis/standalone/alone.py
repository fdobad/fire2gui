

from qgis.PyQt.QtWidgets import QDialog, QApplication
from qgis.gui import QgsFileWidget

app = QApplication([])
new_dialog = QDialog()
new_dialog.resize(400, 300)
file_widget = QgsFileWidget(new_dialog)

new_dialog.show()
