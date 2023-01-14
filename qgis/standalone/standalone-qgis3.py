#!python3
'''
2023 Jan fixed

https://gist.githubusercontent.com/ThomasG77/f711853e5fb81c746d2a1af0b2a9ecf5/raw/6ec0659882352f781953c4a1061ee9e68bb6960a/standalone-qgis3.py
# Code borrowed from https://subscription.packtpub.com/book/application_development/9781783984985/1/ch01lvl1sec18/creating-a-standalone-application
# and upgraded for QGIS 3.0
'''
import sys
from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsProject, QgsRasterLayer, QgsRectangle)
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas
from qgis.PyQt.QtCore import Qt

def main():
    app = QgsApplication([], True)
    # On Linux, didn't need to set it so commented
    # app.setPrefixPath("C:/Program Files/QGIS Brighton/apps/qgis", True)
    app.initQgis()
    canvas = QgsMapCanvas()
    project = QgsProject.instance()
    bridge = QgsLayerTreeMapCanvasBridge(
        project.layerTreeRoot(),
        canvas
    )
    canvas.setWindowTitle("FireRes PyQGIS Standalone Application Example")
    canvas.setCanvasColor(Qt.white)
    crs = QgsCoordinateReferenceSystem("EPSG:3857")
    canvas.setDestinationCrs(crs)
    
    urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
    rlayer2 = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')
    
    if rlayer2.isValid():
        project.addMapLayer(rlayer2)
    else:
        print('invalid layer')
    print(rlayer2.crs().authid())
    #canvas.setExtent(layer_shp.extent())
    #canvas.setLayers([rlayer2, layer_shp])
    #canvas.setExtent(QgsRectangle(-20037508.3427892439067364,-20037508.3427892550826073,
    #                               20037508.3427892439067364, 20037508.3427892439067364))
    #canvas.setLayers([rlayer2])
    print('wtf',canvas.extent())
    canvas.setExtent(QgsRectangle(-7864915.17435287, -3953069.52491695,
                                  -7860093.88926933, -3950024.50275892 ))
    #canvas.zoomToFullExtent()
    #canvas.freeze(True)
    canvas.refresh()
    #canvas.waitWhileRendering()
    canvas.show()
    canvas.setExtent(QgsRectangle(-7864915.17435287, -3953069.52491695,
                                  -7860093.88926933, -3950024.50275892 ))
    print('wtf',canvas.extent())
    #canvas.freeze(False)
    #canvas.repaint()
    
    # register events
    def run_when_project_saved():
        project.write('my_new_qgis_project.qgz')
        print('Saved')
    project.projectSaved.connect(run_when_project_saved)
    
    def run_when_application_state_changed(state):
        print('State changed', state)
    app.applicationStateChanged.connect(run_when_application_state_changed)
    
    exitcode = app.exec()
    QgsApplication.exitQgis()
    sys.exit(exitcode)

if __name__ == '__main__':
    main()
