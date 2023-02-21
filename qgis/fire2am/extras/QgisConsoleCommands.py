import processing
from qgis.core import QgsVectorDataProvider, QgsField, QgsGeometry #, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant
from collections import namedtuple
from datetime import datetime
import numpy as np
print('=== Hello World!',datetime.now().strftime('%H:%M:%S'),'===')

''' QGIS 
    processing is in PYTHONPATH 
    <module 'processing' from '/usr/share/qgis/python/plugins/processing/__init__.py'>
'''
LayerStuff = namedtuple('layerStuff', 'names attr geom id len')
def getVectorLayerStuff( layer) -> namedtuple:
    '''TODO add field_types = [f.typeName() for f in layer.fields()]
    '''
    names = [f.name() for f in layer.fields()]
    attributes = []
    geometry = []
    id = []
    for f in layer.getFeatures():
        attributes += [f.attributes()]
        geometry += [ f.geometry() ]
        id += [ f.id() ]
    return LayerStuff(  names = names, 
                        attr = np.array(attributes), 
                        geom = np.array(geometry), 
                        id = np.array(id),
                        len = len(geometry) )

def pixelstopolygons(layer): 
    '''processing.algorithmHelp('native:pixelstopolygons')
        TODO add params , band=1, field_name='VALUE')
    '''
    tmp = processing.run('native:pixelstopolygons', 
               {'INPUT_RASTER' : layer, 
                'RASTER_BAND' : 1,
                'FIELD_NAME' : 'VALUE', 
                'OUTPUT' : 'TEMPORARY_OUTPUT' })
    return tmp['OUTPUT'] 

def addautoincrementalfield(layer):
    '''processing.algorithmHelp('native:addautoincrementalfield')
    '''
    tmp = processing.run('native:addautoincrementalfield',
           {'FIELD_NAME' : 'index', 
            'GROUP_FIELDS' : [], 
            'INPUT' : layer, 
            'OUTPUT' : 'TEMPORARY_OUTPUT', 
            'SORT_ASCENDING' : True, 
            'SORT_EXPRESSION' : '\"id\"', 
            'SORT_NULLS_FIRST' : True, 
            'START' : 0 })
    return tmp['OUTPUT']

def add2dIndex( layer, x='x', y='y'):
    ''' add integer 2d integer index relative position pos_x pos_y
    '''
    layerStuff = getVectorLayerStuff( layer)
    fields_name = layerStuff.names
    if not (x in fields_name and y in fields_name):
        layer = addxyfields(layer)
        layerStuff = getVectorLayerStuff( layer)
        fields_name = layerStuff.names
    idx = fields_name.index(x)
    idy = fields_name.index(y)
    data = layerStuff.attr
    ''' get unique values for x and y assuming they're aligned '''
    xun = np.unique( data[:,idx] )
    yun = np.unique( data[:,idy] )
    ''' position is index of data in the unique value '''
    # TODO np.isclose(a,b) for floats
    pos_x = [ np.where( xun == p)[0][0] for p in data[:,idx] ]
    pos_y = [ np.where( yun == p)[0][0] for p in data[:,idy] ]
    ''' add calculated arrays '''
    layer.dataProvider().addAttributes([QgsField('pos_x',QVariant.Int)])
    layer.dataProvider().addAttributes([QgsField('pos_y',QVariant.Int)])
    layer.updateFields()
    fields_name = [f.name() for f in layer.fields()]
    idposx = fields_name.index('pos_x')
    idposy = fields_name.index('pos_y')
    for i,feature in enumerate(layer.getFeatures()):
        attrx = { idposx : int(pos_x[i]) }
        attry = { idposy : int(pos_y[i]) }
        layer.dataProvider().changeAttributeValues({feature.id() : attrx })
        layer.dataProvider().changeAttributeValues({feature.id() : attry })
        
def addXYcentroid( layer ):
    ''' add 'center_x' & 'center_y' attr to polyLayer '''
    fields_name = [f.name() for f in layer.fields()]
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.AddAttributes:
        if 'center_x' not in fields_name:
            layer.dataProvider().addAttributes([QgsField('center_x', QVariant.Double)])
        if 'center_y' not in fields_name:
            layer.dataProvider().addAttributes([QgsField('center_y', QVariant.Double)])
        layer.updateFields()
        fields_name = [f.name() for f in layer.fields()]
        fareaidx = fields_name.index('center_x')
        fareaidy = fields_name.index('center_y')
    if caps & QgsVectorDataProvider.ChangeAttributeValues:
        for feature in layer.getFeatures():
            centr = QgsGeometry.centroid(feature.geometry())
            attrx = { fareaidx : centr.asPoint().x() }
            attry = { fareaidy : centr.asPoint().y() }
            layer.dataProvider().changeAttributeValues({feature.id() : attrx })
            layer.dataProvider().changeAttributeValues({feature.id() : attry })

def getVectorLayerStuff( layer) -> namedtuple:
    '''TODO add field_types = [f.typeName() for f in layer.fields()]
    '''
    LayerStuff = namedtuple('layerStuff', 'names attr geom len')
    names = [f.name() for f in layer.fields()]
    attributes = []
    geometry = []
    for f in layer.getFeatures():
        attributes += [f.attributes()]
        geometry += [ f.geometry() ]
    return LayerStuff(  names = names,
                        attr = np.array(attributes),
                        geom = np.array(geometry),
                        len = len(geometry) )

def convertRasterToNumpyArray(layer): #Input: QgsRasterLayer
    values=[]
    provider= layer.dataProvider()
    block = provider.block(1,layer.extent(),layer.width(),layer.height())
    for i in range(layer.width()):
        for j in range(layer.height()):
            values.append(block.value(i,j))
    return np.array(values)

class myarray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return np.array(*args, **kwargs).view(myarray)
    def index(self, value):
        return np.where(self == value)

def listAllProcessingAlgorithms():
    ''' processing must be added to PYTHONPATH
    processing.algorithmHelp('native:pixelstopolygons')

    from qgis import processing
    'native:native:adduniquevalueindexfield' NOT FOUND
    '''
    for alg in QgsApplication.processingRegistry().algorithms():
            print(alg.id(), "->", alg.displayName())

project = QgsProject.instance() 
project
mc = iface.mapCanvas()
mc
layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
layers_byName
layer = iface.mapCanvas().currentLayer()
layer

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

STOP    

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

print('=== Bye World!',datetime.now().strftime('%H:%M:%S'),'===')
