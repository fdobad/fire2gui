import processing
from qgis.core import QgsVectorDataProvider, QgsField, QgsGeometry #, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant
from collections import namedtuple
from datetime import datetime
import numpy as np

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
    fid = []
    for f in layer.getFeatures():
        attributes += [f.attributes()]
        geometry += [ f.geometry() ]
        fid += [ f.id() ]
    return LayerStuff(  names = names, 
                        attr = np.array(attributes), 
                        geom = np.array(geometry), 
                        id = np.array(fid),
                        len = len(geometry) )

def clipRasterLayerByMask(raster, polygon, nodata=-32768):
    ''' Algorithm 'Clip raster by mask layer' 
    gdal:cliprasterbymasklayer -> Clip raster by mask layer
    make sure both layers are saved to disk, & same CRS
    adds new layer to project
    returns filepath str
    '''
    outname = raster.name() + '_clippedBy_' + polygon.name() + '.asc'
    outname = outname.replace(' ','')
    outpath = QgsProject().instance().absolutePath()
    out = os.path.join( outpath, outname )

    tmp = processing.run('gdal:cliprasterbymasklayer', 
            { 'ALPHA_BAND' : False, 'CROP_TO_CUTLINE' : True, 'DATA_TYPE' : 0, 'EXTRA' : '', 'INPUT' : raster, 'KEEP_RESOLUTION' : True, 'MASK' : polygon, 'MULTITHREADING' : True, 'NODATA' : nodata, 'OPTIONS' : '', 'OUTPUT' : out, 'SET_RESOLUTION' : False, 'SOURCE_CRS' : raster.crs(), 'TARGET_CRS' : raster.crs(), 'X_RESOLUTION' : None, 'Y_RESOLUTION' : None })
    iface.addRasterLayer( out, outname)
    return tmp['OUTPUT'] 

def clipVectorByPolygon(layer, polygon):
    ''' gdal:clipvectorbypolygon
    adds new layer to project
    returns filepath str
    '''
    outname = layer.name() + '_clippedBy_' + polygon.name() + '.shp'
    outname = outname.replace(' ','')
    outpath = QgsProject().instance().absolutePath()
    out = os.path.join( outpath, outname )
    tmp = processing.run('gdal:clipvectorbypolygon', 
            { 'INPUT' : layer, 'MASK' : polygon, 'OPTIONS' : '', 'OUTPUT' : out })
            #{ 'INPUT' : layer, 'MASK' : polygon, 'OPTIONS' : '', 'OUTPUT' : 'TEMPORARY_OUTPUT' })
    iface.addVectorLayer(out , ' ', 'ogr') #layer.providerType())
    return tmp['OUTPUT'] 

def clipVectorLayerByExtent(layer, extent, clip=True):
    '''processing.algorithmHelp('native:extractbyextent')
    Extract/clip by extent
             'EXTENT' : extent, #'-70.651805555556,-70.60828703703399,-33.434398148148,-33.411249999998', 
             'INPUT' : layer, #'/home/fdo/dev/fire2am/userFolder/ignitions.shp', 
    '''
    tmp = processing.run('native:extractbyextent', 
            {'CLIP' : clip, 
             'EXTENT' : extent,
             'INPUT' : layer,
             'OUTPUT' : 'TEMPORARY_OUTPUT' })
    return tmp['OUTPUT'] 

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

def routascii(layer, filename='TEMPORARY_OUTPUT'):
    '''returns filename as path string
    Not same format as fire2aascii used files
    processing.algorithmHelp('grass7:r.out.ascii')
    '''
    tmp = processing.run('grass7:r.out.ascii',
           { '-i' : False,
           '-m' : False,
           '-s' : False,
           'GRASS_REGION_CELLSIZE_PARAMETER' : 0,
           'GRASS_REGION_PARAMETER' : None,
           'input' : layer, 
           'null_value' : '*', 
           'output' : filename,
           'precision' : None,
           'width' : None })
    return tmp['OUTPUT']

def buildVirtualRaster( layer, name='vrt'):
    tmp =  processing.run('gdal:buildvirtualraster', { 'ADD_ALPHA' : False, 'ASSIGN_CRS' : layer.crs(), 'EXTRA' : '', 'INPUT' : layer, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PROJ_DIFFERENCE' : False, 'RESAMPLING' : 0, 'RESOLUTION' : 0, 'SEPARATE' : False, 'SRC_NODATA' : '' })
    return QgsRasterLayer( tmp['OUTPUT'], name)


from osgeo import gdal
import tempfile
from pathlib import Path
Path(gpkg_file).touch()

def writeRaster( raster_file, tableName='forestgrids', crs = QgsCoordinateReferenceSystem('IGNF:UTM31ETRS89')):
    fname = tempfile.mktemp( suffix='.gpkg', dir=os.getcwd() )
    gdal.GetDriverByName('GPKG').Create(fname, 1, 1, 1)
    source = QgsRasterLayer( raster_file, 'rasterName', 'gdal')
    source.setCrs(QgsCoordinateReferenceSystem('IGNF:UTM31ETRS89'))
    print('source.isValid()',source.isValid(), source)
    provider = source.dataProvider()
    print('provider.isValid()',provider.isValid(), provider)
    fw = QgsRasterFileWriter(fname)
    fw.setOutputFormat('gpkg')
    fw.setCreateOptions(['RASTER_TABLE='+str(tableName), 'APPEND_SUBDATASET=YES'])
    pipe = QgsRasterPipe()
    print( pipe.set(provider.clone()) )
    projector = QgsRasterProjector()
    projector.setCrs(crs, crs)
    if pipe.insert(2, projector) is True:
        if fw.writeRaster(pipe, provider.xSize(),provider.ySize(),provider.extent(),crs) == 0:
            print("ok")
        else:
            print("error")

def writeRaster(layer,  out_file = '/tmp/reprojected_raster.asc', 
                        dest_crs_def = "EPSG:24879"):
    ''' 
    tr = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                QgsCoordinateReferenceSystem("EPSG:24879"), 
                                QgsProject.instance())
                                
    assert QgsRasterFileWriter.driverForExtension('asc') == 'AAIGrid'
    No es texto
    #provider.block(1, provider.extent(), source.width(), source.height()).data(),
    '''
    
    if layer.crs() == QgsCoordinateReferenceSystem():
        layer.setCrs( QgsCoordinateReferenceSystem("EPSG:4326") )
        #layer.setCrs( QgsProject.instance().crs() )
        print('source layer without crs set to ', layer.crs())
    
    orig_crs = layer.crs()
    dest_crs = QgsCoordinateReferenceSystem(dest_crs_def)
    
    
    tr = QgsCoordinateTransform(orig_crs, dest_crs, QgsProject.instance())
    file_writer = QgsRasterFileWriter(out_file)
    # .setOutputFormat('asc')
    pipe = QgsRasterPipe()
    provider = layer.dataProvider()
    projector = QgsRasterProjector()
    projector.setCrs(orig_crs, dest_crs)    
    if not pipe.set(projector):
        print('error pipe setting projector')
    if not pipe.set(provider.clone()):
        print('error pipe setting provider')
    #renderer = layer.renderer()
    #pipe.set(renderer.clone())
    if not file_writer.writeRaster(pipe,
                                 provider.xSize(),
                                 provider.ySize(),
                                 tr.transform(provider.extent()),
                                 dest_crs):
        print('error file writing asc')
    
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

def getVectorLayerStuff0( layer) -> namedtuple:
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

    '''
    layer = iface.mapCanvas().currentLayer()
    layer, provider, block, qByteArray[:8], npArr, data
    '''

def convertRasterToNumpy30xSLOWER(layer): #Input: QgsRasterLayer
    '''
    %time it convertRasterToNumpy30xSLOWER(layer)
    %time it convertRasterToNumpyArray(layer)
    '''
    provider= layer.dataProvider()
    block = provider.block(1,layer.extent(),layer.width(),layer.height())
    values = [[]]
    for j in range(layer.height()):
        values += []
        for i in range(layer.width()):
            values[-1] += [ block.value(j,i) ]
    return np.array(values)

def convertRasterToNumpyArray(layer): #Input: QgsRasterLayer
    provider = layer.dataProvider()
    block = provider.block(1, layer.extent(), layer.width(), layer.height())
    qByteArray = block.data()
    npArr = np.frombuffer( qByteArray)  #,dtype=float)
    return npArr.reshape( (layer.height(),layer.width()))
    
class myarray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return np.array(*args, **kwargs).view(myarray)
    def index(self, value):
        int : return np.where(self == value)
        floats : return np.where( np.isclose( self, value))

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

groupName="test group"
root = QgsProject.instance().layerTreeRoot()
group = root.addGroup(groupName)

fd, tname = tempfile.mkstemp()
raster = QgsRasterLayer(tname, 'tmp')
provider = raster.dataProvider()
provider.setEditable(True)

block = provider.block(1, layer.extent(), layer.width(), layer.height())

tdir = '/home/fdo/source/C2FSB/results/Grids/Grids1/'
data = np.loadtxt( tdir+'ForestGrid02.csv', dtype=np.float64, delimiter=',')
bites = QByteArray( data.tobytes() ) 
block.setData( bites)

group.insertChildNode(0,raster)
QgsProject.instance().addMapLayer(polyLayer)


# cookbook/raster
fd, tname = tempfile.mkstemp()
raster = QgsRasterLayer(tname, 'tmp')

tdir = '/home/fdo/source/C2FSB/results/Grids/Grids1/'
data = np.loadtxt( tdir+'ForestGrid02.csv', dtype=np.float64, delimiter=',')
bites = QByteArray( data.tobytes() ) 
block = QgsRasterBlock(Qgis.Byte, w, h)
block.setData( bites)

provider = raster.dataProvider()
provider.setEditable(True)
provider.writeBlock(block, 1, 0, 0)
provider.setEditable(False)

# write
pipe = QgsRasterPipe()
pipe.set(providerclone)
file_writer.writeRaster(pipe, provider.xSize(),provider.ySize(),provider.extent(),provider.crs())


layer.setCrs( QgsCoordinateReferenceSystem(4326))

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

def matchPointToRasterCellsCoords(raster, point):
    ''' raster extent -> 2 linspaces -> indexOf
    indexOf : np.where( np.isclose( point_x, x_linspace))
    p.geometry().asPoint().x()
    '''
    re = raster.extent()
    xspace = np.linspace( re.xMinimum(), re.xMaximum(), raster.width() )
    yspace = np.linspace( re.yMinimum(), re.yMaximum(), raster.height() )
    px, py =  point.x(), point.y()
    xcell = np.where( np.isclose( px, xspace))
    ycell = np.where( np.isclose( py, yspace))
    return xcell, ycell

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

def id2xy( idx, w=6, h=4):
    ''' idx: index, w: width, h:height '''
    return idx%w, idx//w 

def xy2id( x, y, w, h):
    ''' x-> w: width, y-> h:height '''
    return y*w+x

def id2uglyId( idx, w, h):
    return w*(h-idx//w) - (w-idx-1)%w

def xy2uglyXy( x, y, w, h):
    ''' flipMinusOne i: index, w: width, h:height '''
    return (x+1, h-y+1)

def uglyXy2xy( x, y, w, h):
    return (x-1, h-y+1)

def uglyId2xy( uid, w, h):
    uid -= 1
    return uid%w, h-uid//w-1

def testTransforms( w=6, h=4):
    c = 0
    for j in range(h):
        print('')
        for i in range(w):
            #print(c,i,j,end='\t')
            assert xy2id( i, j, w, h) == c
            assert np.all( id2xy( c, w, h) == (i,j))
            assert np.all( uglyId2xy( id2uglyId( c, w, h), w, h) == (i,j))
            xu, yu = xy2uglyXy( i, j, w, h)
            assert np.all( uglyXy2xy( xu, yu, w, h) == (i,j))
            c+=1

testTransforms( w=6, h=4)
def testTransforms( w=6, h=4):
    c = 0
    for j in range(h):
        for i in range(w):
            assert np.all( id2cellxy(c) == (i,j) )
            assert cellxy2id(i,j) == c
            print(c,i,j,id2cellxy(c),cellxy2id(i,j), cellxy2UglyId(i,j))
            c+=1
    print('ok')
