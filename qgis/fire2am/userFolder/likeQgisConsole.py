#!/bin/env python3
#REPLENV: /home/fdo/pyenv/qgis

#%cd ../userFolder/

from qgis.PyQt.QtCore import QVariant
from qgis.core import *
import qgis.utils

app = QgsApplication([], True)
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()
#QgsApplication.exitQgis()

''' TODO fix using from standalone
from qgis import processing
# list all
for alg in QgsApplication.processingRegistry().algorithms():
        print(alg.id(), "->", alg.displayName())
'''
def log(*args, plugin='My Plugin'):
    '''
    log = lambda m: QgsMessageLog.logMessage(m,'My Plugin') 
    log('My message')
    '''
    QgsMessageLog.logMessage(str(args), plugin) 
    print(plugin,':', *args)
log('My message', 'otro')

project = QgsProject.instance() #empty project
project = QgsProject.read('project.qgz') #empty project
#canvas = QgsMapCanvas() DEPRECATEd ????

layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
log(layers_byName )

layer = QgsVectorLayer('ignitions.shp','ignitions','ogr')
rlayer = QgsRasterLayer('elevation.asc')

log( rlayer.width(), rlayer.height()

STOP

layer.dataProvider().addAttributes([QgsField('idx', QVariant.Int )])
layer.dataProvider().addAttributes([QgsField('idy', QVariant.Int )])

polyLayer = processing.run('native:pixelstopolygons', 
   {'INPUT_RASTER' : rlayer, 
    'RASTER_BAND' : 1,
    'FIELD_NAME' : 'VALUE', 
    'OUTPUT' : 'TEMPORARY_OUTPUT' })
polyLayer = polyLayer['OUTPUT'] 

QgsApplication.exitQgis()
