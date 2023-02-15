#!/usr/bin/env python3

from qgis.core import (
    QgsApplication, QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry)
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout


class MyDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self)
        self.parent = parent
        self.setLayout(QVBoxLayout())

        project = QgsProject()
        canvas = QgsMapCanvas()
        bridge = QgsLayerTreeMapCanvasBridge(
            project.layerTreeRoot(),
            canvas
        )
        bridge.setCanvasLayers()
        self.layout().addWidget(canvas)

        layer = QgsVectorLayer(
            'Point?'
            'crs=epsg:4326&'
            'field=id:integer&field=name:string(20)&index=yes',
            'layer', 'memory')

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt('POINT(10 10)'))
        feature.setAttributes([1, 'Point'])
        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        layer.updateExtents()
        project.addMapLayer(layer)
        canvas.zoomToFullExtent()
        self.exec_()


if __name__ == '__main__':
    QgsApplication.setPrefixPath('/application/path/to/adapt', True)
    application = QgsApplication([], True)
    application.initQgis()
    dialog = MyDialog(application)
    application.exitQgis()
