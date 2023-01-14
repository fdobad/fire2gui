#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
# Copyright (C) 2022 Fernando Badilla  
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------
from PyQt5.QtWidgets import QAction, QMessageBox
import matplotlib.pyplot as plt
import numpy as np
#from matplotlib.widgets import Slider, Button
#from qgis.utils import iface
from qgis.core import (
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsProject,
        QgsPointXY,
        )
#        QgsApplication,
#from qgis import processing
import elevation
#import rasterio
import os.path

class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('fireMin!', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        print('hello printy debug')
        project = QgsProject.instance()
        projectPath = project.homePath()
        ## user view
        extent3857 = self.iface.mapCanvas().extent()
        ##print('displayed extent is', extent3857 )
        center3857 = extent3857.center()
        ##print('displayed center is', center3857 )
        ## elevation 
        ### transform
        crsSrc = QgsCoordinateReferenceSystem("EPSG:3857")
        crsDest = QgsCoordinateReferenceSystem("EPSG:4326")
        transformContext = project.transformContext()
        xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)
        ## forward transformation: src -> dest
        center4326 = xform.transform(center3857)
        extent4326 = xform.transform(extent3857)
        print("Transformed center:", center4326)
        print("Transformed extent:", extent4326)
        ## inverse transformation: dest -> src
        ##pt2 = xform.transform(pt1, QgsCoordinateTransform.ReverseTransform)
        ##print("Transformed back:", pt2)
        ##
        ### get data
        ymax = extent4326.yMaximum()
        ymin = extent4326.yMinimum()
        xmax = extent4326.xMaximum()
        xmin = extent4326.xMinimum()
        print(xmin,ymin,xmax,ymax)
        output = os.path.join( projectPath, 'dem.tif')
        #print('overriding',output)
        # TODO check if dem.tif has the same extent, then not request
        elevation.clip( (xmin,ymin,xmax,ymax), product='SRTM1', output=output)
        self.iface.addRasterLayer(output, "dem 30m")
        ##'''
        ##print('list algo')
        ##for alg in QgsApplication.processingRegistry().algorithms():
        ##    if 'gdal' in alg.displayName():
        ##        print(alg.id(), "->", alg.displayName())
        ##gdal:translate -> Translate (convert format)
        ##!gdal_translate -tr 0.0009259259266657407 0.0009259259266657407 -of AAIGrid dem.tif test.asc
        ##'''
        ##dataset = rasterio.open('dem.tif')
        #dataset = rasterio.open(output)
        #res = np.array(dataset.res)
        #res100 = 10/3*res
        ##
        QMessageBox.information(None, 'FirePlugin QMessageBox', 'Hello World!')
        print('bye printy debug')
