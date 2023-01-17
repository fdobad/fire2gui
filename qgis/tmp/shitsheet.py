'''
__QGIS plugin development shitsheet__
'''
# get the ignition point in a layer
layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values() }
il = layers_byName['ignition']
[ f for f in il.getFeatures()][0].geometry()

# qgis console has this preloaded
from qgis.core import *
import qgis.utils

# main objects
iface
QgsProject

# installation path
QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)
>>> ['/home/fdo/.local/share/QGIS/QGIS3', '/usr/local/share/QGIS/QGIS3', '/usr/share/QGIS/QGIS3']
Only .local... works!

# Layers
layers_byIDs = QgsProject.instance().mapLayers()
layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}

# add raster layer
iface.addRasterLayer(path_to_tif_or_asc_file, "layer_name")

# Vector operation
 QgsGeometryUtils.midpoint(QgsPoint,QgsPoint)
rlayer = layers['test']
rect = rlayer.extent()
centerPoint = rect.center()

# colorshade viridis 
fcn = QgsColorRampShader()
fcn.setColorRampType(QgsColorRampShader.Interpolated)
lst = [ QgsColorRampShader.ColorRampItem(0, QColor(68,1,84)),
      QgsColorRampShader.ColorRampItem(255, QColor(253,231,37)) ]
fcn.setColorRampItemList(lst)
shader = QgsRasterShader()
shader.setRasterShaderFunction(fcn)
renderer = QgsSingleBandPseudoColorRenderer(rlayer.dataProvider(), 1, shader)
rlayer.setRenderer(renderer)
rlayer.triggerRepaint()

# displaying a window
from PyQt5 import QtWidgets

def window():
    w = QtWidgets.QWidget()
    b = QtWidgets.QLabel(w)
    b.setText("Hello World!")
    w.setGeometry(100,100,200,50)
    b.move(50,20)
    w.setWindowTitle("PyQt")
    return w

w = window()
w.show()

# display window on change
lyr=iface.activeLayer()
def myFunction(selFeatures):
   print(str(len(selFeatures)) + " features were selected: " + str(selFeatures))
   QMessageBox.information(None, 'title', str(len(selFeatures)) + " features were selected: " + str(selFeatures))
lyr.selectionChanged.connect(myFunction)

# qmessagelog
# msg, LogMessages Panel Name, level
QgsMessageLog.logMessage("Your plugin code has been executed correctly", 'FirePlugin', level=Qgis.Info)
QgsMessageLog.logMessage("Your plugin code might have some problems", 'FirePlugin', level=Qgis.Warning)
QgsMessageLog.logMessage("Your plugin code has crashed!", 'FirePlugin', level=Qgis.Critical)
