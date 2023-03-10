
import os
from .fire2am_utils import check, aName, log, get_params, , randomDataFrame, csv2rasterInt16, mergeVectorLayers, cellIds2matchingLayer
from .qgis_utils import check_gdal_driver_name, id2uglyId, uglyId2xy, matchPointLayer2RasterLayer
''' getting layers '''
layer = iface.mapCanvas().currentLayer()
# { name : layer }
layers = { l.name():l for l in QgsProject.instance().mapLayers().values()}
# { id : layer }
layers_id = QgsProject.instance().mapLayers()

''' add layer from file '''
rasterLayer = QgsRasterLayer('GPKG:/home/fdo/source/C2FSB/data/Vilopriu_2013/raster.gpkg:tableName')
QgsProject.instance().addMapLayer(layer)

''' common properties '''
''' crs '''
aCrs = QgsCoordinateReferenceSystem('IGNF:UTM31ETRS89')
bCrs = layer.crs()
layer.setCrs( aCrs)
layer.setCrs( QgsCoordinateReferenceSystem(4326))

''' extent '''
e = layer.extent()

project = QgsProject.instance() 
project
mc = iface.mapCanvas()
mc
layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
layers_byName
layer = iface.mapCanvas().currentLayer()
layer

def createRasterFloat(  filename = 'testpy.tif', 
                        extent = layer.extent(), 
                        crs = layer.crs(),
                        data = None ):
    if not data:
        data = np.zeros((3,4), dtype=np.float64)
        data[0,0] = 1.0
    if not date.dtype == np.float64:
        data = np.float64( data)
    h,w = data.shape()
    # set 
    bites = QByteArray( data.tobytes() ) 
    block = QgsRasterBlock( Qgis.Float64, w, h)
    block.setData( bites)
    if not block.isValid():
        return False, 'block invalid'
    # write
    # 1 ok
    fw = QgsRasterFileWriter( filename )
    # 2 nop
    #fw = QgsRasterFileWriter('testpy.asc')
    #fw.setOutputFormat('AAIGrid')
    # 3 Float64 not supported
    #fw = QgsRasterFileWriter('test.gpkg')
    #fw.setOutputFormat('gpkg')
    #fw.setCreateOptions(['RASTER_TABLE=testpy', 'APPEND_SUBDATASET=YES'])
    provider = fw.createOneBandRaster( Qgis.Float64, w, h, extent, crs )
    ''' mark zeros as nodata '''
    provider.setNoDataValue(1, -1.0)
    if not provider.isValid():
        return False, 'provider invalid'
    if not provider.isEditable():
        return False, 'provider not editable'
    if not provider.writeBlock( block, 1, 0, 0):
        return False, 'provider failed to write block'
    return True, ''

def checkPointsInRasterExtent( raster, points):
    ''' returns a list indicating True/False for each point
    for p in points.getFeatures():
        if raster.extent().contains(  p.geometry().asPoint() ) :
            print(p, 'ok')
        else:
            print(p, 'no')
    '''
    re = raster.extent()
    return [ re.contains(  p.geometry().asPoint() ) for p in points.getFeatures() ]

def matchPointLayer2RasterLayer( raster, point):
    pointsIn = checkPointsInRasterExtent( raster, point) 
    re = raster.extent()
    xspace = np.linspace( re.xMinimum(), re.xMaximum(), raster.width() )
    yspace = np.linspace( re.yMinimum(), re.yMaximum(), raster.height())
    pt = [ p.geometry().asPoint() for p in point.getFeatures() ]
    pts = [ [p.x(),p.y()] for p in pt ]
    cellxy = []
    cellid = []
    dx = xspace[1] - xspace[0]
    dy = yspace[1] - yspace[0]
    for i,(px,py) in enumerate(pts):
        if pointsIn[i]:
            cx = np.where( np.isclose( xspace, px, atol=dx/2, rtol=0))[0][0]
            cy = np.where( np.isclose( yspace, py, atol=dy/2, rtol=0))[0][0]
            #cx = np.where( np.isclose( xspace, px, atol=0, rtol=dx/px/2))[0][0]
            #cy = np.where( np.isclose( yspace, py, atol=0, rtol=dy/py/2))[0][0]
            cellxy += [[cx,cy]]
            cellid += [ cx + raster.height()*cy ]
            #print('px',px,xspace[cx],cx)
            #print('py',py,xspace[cy],cy)
            #print('id',cellid[-1])
        else:
            cellxy += [[-1,-1]]
            cellid += [ -1 ]
    return cellid, cellxy

''' adding layer group '''
groupName="test group"
root = QgsProject.instance().layerTreeRoot()
group = root.addGroup(groupName)
group.insertChildNode(0,raster)
QgsProject.instance().addMapLayer(polyLayer)


print('layer type', layer.type())
if QgsMapLayerType.VectorLayer == layer.type():
    field_names = [f.name() for f in layer.fields()]
    field_names
    field_types = [f.typeName() for f in layer.fields()]
    field_types
    layerStuff = getVectorLayerStuff( layer)
    # TODO
    #f.attributeMap()
    #f.attributes()[field_names.index('hey')]
elif QgsMapLayerType.RasterLayer == layer.type():
    layerData = convertRasterToNumpyArray(layer)
else:
    print('nothing done')

layer.setName('layer_name')
QgsProject.instance().addMapLayer(polyLayer)
QgsVectorFileWriter.writeAsVectorFormat(ignition_cells, "ignition_cells.gpkg")

import os.path
plugin_dir = '/home/fdo/dev/fire2am/img'
polyLayer.loadNamedStyle(os.path.join( plugin_dir, 'instanceGrid_layerStyle.qml'))

''' in which cell a ignition point belongs '''
ignitions = layers_byName['ignitions']
for ig in ignitions.getFeatures():
    for p in polyLayer.getFeatures():
        if p.geometry().contains(ig.geometry()):
            polyLayer.select(p.id())
            #print(p.attributes(),ig.geometry())

ignition_cells = polyLayer.materialize(QgsFeatureRequest().setFilterFids(polyLayer.selectedFeatureIds()))

ignitions = layers_byName['ignition points']
raster =  layers_byName['model_21_ascii']
from itertools import combinations
def checkAllLayersHaveSameExtent( layers = QgsProject.instance().mapLayers()):
    for layer1,layer2 in combinations( layers, 2):
        if not layer1.extent() == layer2.extent():
            return False, (layer1.name(),layer2.name())
    return True, _

''' v1 for standalone use '''
from qgis.testing import start_app
app = start_app()
''' v2 for standalone use '''
from qgis.core import QgsApplication
app = QgsApplication([], True)
app.initQgis()

from osgeo import gdal
import tempfile
from pathlib import Path
from glob import glob
import sys
from qgis.core import Qgis, QgsApplication, QgsRasterLayer, QgsRasterBlock, QgsMapLayerType
from qgis.PyQt.QtCore import QByteArray
from tempfile import mkstemp

from qgis.core import Qgis, QgsRasterFileWriter, QgsRasterBlock
from qgis.PyQt.QtCore import QByteArray
import numpy as np
def csv2rasterInt16( extent, layerName, filepath = 'result/Grids/Grids1/ForestGrid04.csv', crs = QgsCoordinateReferenceSystem('IGNF:UTM31ETRS89') ):
    data = np.loadtxt( filepath, dtype=np.int16, delimiter=',')
    h,w = data.shape
    bites = QByteArray( data.tobytes() ) 
    block = QgsRasterBlock( Qgis.CInt16, w, h)
    block.setData( bites)
    if not block.isValid():
        return False
    fw = QgsRasterFileWriter('rastersInt16.gpkg')
    fw.setOutputFormat('gpkg')
    fw.setCreateOptions(['RASTER_TABLE='+layerName, 'APPEND_SUBDATASET=YES'])
    provider = fw.createOneBandRaster( Qgis.Int16, w, h, extent, crs )
    if not provider.isValid():
        return False
    if not provider.isEditable():
        return False
    if not provider.writeBlock( block, 1, 0, 0):
        return False
    return True

from itertools import islice
def csv2ascList( file_list = ['ForestGrid00.csv','ForestGrid01.csv'], header_file = 'elev.asc' ):
    with open( head_file, 'r') as afile:
        header = list(islice(afile, 6))
    for afile in file_list:
        fname = afile[:-4]
        csv2ascFile( in_file = afile, header = header, out_file = fname+'.asc')

def csv2ascFile( in_file = 'ForestGrid00.csv', 
        header = ['ncols 508\n', 'nrows 610\n', 'xllcorner 494272.38261041\n', 'yllcorner 4652115.6527613\n', 'cellsize 20\n', 'NODATA_value -9999\n'],
        out_file = 'ForestGrid00.asc'):
    with open(out_file, 'w') as outfile:
        outfile.writelines(header)
    with open( in_file, 'rb', buffering=0) as infile:
        with open(out_file, 'ab') as outfile:
            outfile.writelines(infile.readlines().replace(b',',b' ')

def rasterFromNpArray():
    data = np.array([ np.loadtxt(f, dtype=np.float64, delimiter=',') for f in glob('Grids1/*csv')])
    p,h,w = data.shape
    
    bites = QByteArray( data[1].ravel().tobytes() ) 
    
    block = QgsRasterBlock( Qgis.CFloat64, w, h)
    block.setData( bites)
    
    fd, fname = mkstemp(suffix='.tif')
    r = QgsRasterLayer(fname,'name')
    dp = r.dataProvider()


from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsProject, QgsRasterLayer, QgsRectangle)
from qgis.core import Qgis

'gdal:buildvirtualraster'


    

tdir = '/home/fdo/source/C2FSB/data/Vilopriu_2013/result/Grids/Grids1/'
data = np.loadtxt( tdir+'ForestGrid02.csv', dtype=np.float64, delimiter=',')
print('data ',data.shape)
bites = QByteArray( data.tobytes() ) 
bites = QByteArray( data.ravel().tobytes() ) 
assert np.dot( *data.shape) * 8 == len(bites)

#layer = iface.mapCanvas().currentLayer()
base = iface.mapCanvas().currentLayer()
assert np.all( data.shape == (base.height(), base.width()))

#provider = layer.dataProvider()
#provider = base.dataProvider()
prov = base.dataProvider()
provider = prov.clone()

block = provider.block(1, base.extent(), base.width(), base.height())
QgsRasterBlock(dataType: Qgis.DataType, width: int, height: int)
#block = QgsRasterBlock( Qgis.Byte, base.height(), base.width())
#block = QgsRasterBlock( Qgis.Byte, base.width(), base.height())
block = QgsRasterBlock( Qgis.Byte, layer.width(), layer.height())
block.setData( bites)

if not provider.setEditable(True):
    print('error enabling editing')
if not provider.writeBlock(block,1,0,0):
    print('error writing block')
if not provider.setEditable(False):
    print('error disabling editing')


out_file='result/grid.tif'
file_writer = QgsRasterFileWriter(out_file)

pipe = QgsRasterPipe()
if not pipe.set(provider):
    print('error pipe setting provider')
if not file_writer.writeRaster(pipe, provider.xSize(), provider.ySize(), provider.extent(), provider.crs()):
    print('error file writer')

def writeRaster(layer, data):
    fd, tname = tempfile.mkstemp(suffix='asc')
    file_writer = QgsRasterFileWriter(tname)

    pipe = QgsRasterPipe()
    or_provider = layer.dataProvider()
    provider = or_provider.clone()  

    bites = QByteArray( data.ravel().tobytes() ) 
    block = provider.block(1, layer.extent(), layer.width(), layer.height())
    if not block.setData( bites):
        return print('error setData')
    provider.setEditable(True)
    provider.writeBlock(block, 1, 0, 0)
    provider.setEditable(False)

    projector = QgsRasterProjector()
    projector.setCrs(layer.crs(), layer.crs())    

    if not pipe.set(projector):
        print('error pipe setting projector')
    if not pipe.set(provider):
        print('error pipe setting provider')
    #renderer = layer.renderer()
    #pipe.set(renderer.clone())
    if not file_writer.writeRaster(pipe,
                                 provider.xSize(),
                                 provider.ySize(),
                                 tr.transform(provider.extent()),
                                 layer.crs()):
        print('error file writing asc')

r = iface.mapCanvas().currentLayer()
p = iface.mapCanvas().currentLayer()

p.crs() == r.crs()


xs = np.linspace( re.xMinimum(), re.xMaximum(), r.width() )
ys = np.linspace( re.yMinimum(), re.yMaximum(), r.height() )

pt = [ pt.geometry().asPoint() for pt in p.getFeatures() ]
px = [ pts.x() for pts in pt ]
py = [ pts.y() for pts in pt ]
pts = [ ( pts.x(), pts.y()) for pts in pt ] 

from glob import glob
import os
import re

file_list = glob('**/*asc') + glob('*asc')

if file_list is []:
    print('empty')

#    '' : '',
file2layer = {
    'model' : 'fuels',
    'mdt' : 'elevation',
    'cbh' : 'cbh',
    'cbd' : 'cbd',
    'fcc' : 'fcc',
    }


for key,val in file2layer.items():
    #pattern = '^a...s$'
    pattern = '.*{}.*asc$'.format(key)
    for afile in file_list:
        result = re.match(pattern, os.path.basename(afile))
        if result:
            print(pattern, result.string)

def setInitialSelectedLayers():
    layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
    for key,val in file2layer.items():
        pattern = '.*{}.*asc$'.format(key)
        for lname,layer in layers_byName.items():
            result = re.match(pattern, lname)
            if result:
                cmb = 'layerComboBox_'+lname
                self.dlg.cmb.setLayer(layer)
                print(pattern, result.string)
