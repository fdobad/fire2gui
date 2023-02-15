import sys
from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsProject, QgsRasterLayer, QgsRectangle)
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas
from qgis.PyQt.QtCore import Qt
'''
#REPLENV: /home/fdo/pyenv/qgis
# usage

# setup
1. open qgis
2. open/create a project

# ignition points

1. Create 'New Shape File Layer', name it 'ignitions' or similar
(all other options in default Geometry type: Point)

2. Add points: 'Toggle Editing' > 'Add Point Feature' > click on map ... > un'Toggle Editing'

3. 'Processing ToolBox' > 'Raster pixels to points' > 
	build a point layer from elevation or fuels > 'Vector Points' will be the new layer

3. 'Processing ToolBox' > 'Distance to nearest hub (points)' >
	build a layer indicating the nearest point between 'ignitions' and 'Vector Points' >
	'Hub distance' will be the new layer

4.
'''
layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
hd = layers_byName['Hub distance']
for f in hd.getFeatures():
	print(f.fields(), f.attributes(), f.geometry())
	break


class QgsStuff(QgsApplication):
    def __init__(self):
        super( QgsApplication, self).__init__([],True)
        #self.app = QgsApplication([], True)
        #self.app = app.initQgis()
        self.initQgis()
        #self.project = QgsProject.instance()
        self.project = QgsProject().read('project.qgz')
        self.canvas = QgsMapCanvas()
        self.bridge = QgsLayerTreeMapCanvasBridge(
                 project.layerTreeRoot(),
                 canvas
             )
        self.canvas.setWindowTitle("FireRes PyQGIS Standalone Application Example")
a = QgsStuff()

