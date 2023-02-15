#!/bin/env python3
#REPLENV: /home/fdo/pyenv/qgis

#%cd ../userFolder/

from qgis.PyQt.QtCore import QVariant
from qgis.core import *
import qgis.utils

from qgis import processing
''' list all
for alg in QgsApplication.processingRegistry().algorithms():
        print(alg.id(), "->", alg.displayName())
'''

app = QgsApplication([], True)
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()
#QgsApplication.exitQgis()

def log(*args, plugin='My Plugin'):
    '''
    log = lambda m: QgsMessageLog.logMessage(m,'My Plugin') 
    log('My message')
    '''
    QgsMessageLog.logMessage(str(args), plugin) 
    print(plugin,':', *args)
log('My message', 'otro')

project = QgsProject.instance() #empty project
#canvas = QgsMapCanvas() DEPRECATEd ????

layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
log(layers_byName )

#layer = QgsVectorLayer('path.shp','myshapefile','ogr')

rlayer = QgsRasterLayer('elevation.asc')
log( rlayer.width(), rlayer.height()

# only in qgis console
log( processing.algorithmHelp('native:pixelstopolygons') )
polyLayer = processing.run('native:pixelstopolygons', 
   {'INPUT_RASTER' : rlayer, 
    'RASTER_BAND' : 1,
    'FIELD_NAME' : 'VALUE', 
    'OUTPUT' : 'TEMPORARY_OUTPUT' })
polyLayer = polyLayer['OUTPUT'] 

