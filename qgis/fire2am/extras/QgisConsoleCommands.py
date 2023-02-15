from datetime import datetime
import numpy as np
print('=== Hello World!',datetime.now().strftime('%H:%M:%S'),'===')

class myarray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return np.array(*args, **kwargs).view(myarray)
    def index(self, value):
        return np.where(self == value)

project = QgsProject.instance() 
#mc = iface.mapCanvas()
#print(mc)
layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
print(layers_byName)

#field_names = [f.name() for f in layer.fields()]
#field_types = [f.typeName() for f in layer.fields()]
#f.attributeMap()
#f.attributes()[field_names.index('hey')]

''' list all 
from qgis import processing
for alg in QgsApplication.processingRegistry().algorithms():
        print(alg.id(), "->", alg.displayName())

'native:native:adduniquevalueindexfield' NOT FOUND
'''

''' asc layer to polygons 
 TODO change 'TEMPORARY_OUTPUT' for vector file 'd:/test.shp'
'''
#processing.algorithmHelp('native:pixelstopolygons')
polyLayer = processing.run('native:pixelstopolygons', 
               {'INPUT_RASTER' : 'elevation.asc', 
                'RASTER_BAND' : 1,
                'FIELD_NAME' : 'VALUE', 
                'OUTPUT' : 'TEMPORARY_OUTPUT' })
polyLayer = polyLayer['OUTPUT'] 

#processing.algorithmHelp('native:pixelstopoints')
pointLayer = processing.run('native:pixelstopoints', 
               {'INPUT_RASTER' : 'elevation', 
                'RASTER_BAND' : 1,
                'FIELD_NAME' : 'VALUE', 
                'OUTPUT' : 'TEMPORARY_OUTPUT' })
pointLayer = pointLayer['OUTPUT'] 

from collections import namedtuple
LayerStuff = namedtuple('layerStuff', 'names attr geom len')
def getVectorLayerStuff( layer) -> namedtuple:
    '''TODO add field_types = [f.typeName() for f in layer.fields()]
    '''
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
    
pointLayer = addautoincrementalfield(pointLayer)
polyLayer = addautoincrementalfield(polyLayer)

def addxyfields(layer):
    '''processing.algorithmHelp('native:addxyfields')
    '''
    tmp = processing.run('native:addxyfields',
           {'CRS' : layer, 
            'INPUT' : layer, 
            'OUTPUT' : 'TEMPORARY_OUTPUT', 
            'PREFIX' : '' })
    return tmp['OUTPUT']

pointLayer = addxyfields(pointLayer)

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
        attrx = { idposx : pos_x[i] }
        attry = { idposy : pos_y[i] }
        layer.dataProvider().changeAttributeValues({feature.id() : attrx })
        layer.dataProvider().changeAttributeValues({feature.id() : attry })
        
''' add 'center_x' & 'center_y' attr to polyLayer '''
def addXYcentroid( layer ):
    fields_name = [f.name() for f in layer.fields()]
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.AddAttributes:
        if 'center_x' not in fields_name:
            layer.dataProvider().addAttributes([QgsField('center_x', QVariant.Int)])
        if 'center_y' not in fields_name:
            layer.dataProvider().addAttributes([QgsField('center_y', QVariant.Int)])
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

addXYcentroid( polyLayer )

add2dIndex( polyLayer, x='center_x', y='center_y')
add2dIndex( pointLayer)

pointStuff = getVectorLayerStuff(pointLayer)
polyStuff = getVectorLayerStuff(polyLayer)

''' in which cell a ignition point belongs '''
ignitions = layers_byName['ignitions']
for ig in ignitions.getFeatures():
    for p in polyLayer.getFeatures():
        if p.geometry().contains(ig.geometry()):
            polyLayer.select(p.id())
            #print(p.attributes(),ig.geometry())

polyLayer.setName('ignitions_grid')
QgsProject.instance().addMapLayer(polyLayer)

QgsVectorFileWriter.writeAsVectorFormat(polyLayer, "ignitions_grid.gpkg")

print('=== Bye World!',datetime.now().strftime('%H:%M:%S'),'===')
