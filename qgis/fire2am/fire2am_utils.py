#!/usr/bin/env python3
#REPLENV: /home/fdo/pyenv/qgis
from pandas import DataFrame, Series
import numpy as np
import os

'''CONSTANTS'''
aName = 'fire2am'


''' QGIS 
    processing is in PYTHONPATH 
    <module 'processing' from '/usr/share/qgis/python/plugins/processing/__init__.py'>
'''

from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsFeature, QgsPointXY, QgsGeometry #QgsPoint, 
def cellIds2matchingLayer( ignitionPoints, rasterLayer, geo_package_file='outputs.gpkg', layerName='ignition points'):
    rex = rasterLayer.extent()
    w, h = rasterLayer.width(), rasterLayer.height()
    xs = np.linspace( rex.xMinimum(), rex.xMaximum(), w+1 )
    ys = np.linspace( rex.yMinimum(), rex.yMaximum(), h+1 )
    dx = xs[1]-xs[0]
    dy = ys[1]-ys[0]
    
    pts = []
    for p in ignitionPoints:
        x,y = id2cellxy( p, w, h)
        f = QgsFeature()
        #f.setGeometry( QgsPoint( xs[x]+dx/2, ys[y]+dy/2)) 
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(xs[x]+dx/2, ys[y]+dy/2)))
        pts += [ f]
    
    vectorLayer = QgsVectorLayer( 'point', layerName, 'memory')
    ret, val = vectorLayer.dataProvider().addFeatures(pts)
    print('addFeatures',ret, val)
    
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = 'GPKG'
    options.layerName = layerName
    if os.path.exists(geo_package_file):
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
    else:
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
    ret, val = QgsVectorFileWriter.writeAsVectorFormat( vectorLayer , geo_package_file, options)
    print('VectorFileWriter', ret, val)

from qgis.core import Qgis, QgsRasterFileWriter, QgsRasterBlock, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import QByteArray
def csv2rasterInt16( extent, layerName, filepath = 'result/Grids/Grids1/ForestGrid04.csv', crs = QgsCoordinateReferenceSystem('IGNF:UTM31ETRS89'), outpath= 'rastersInt16.gpkg'):
    data = np.loadtxt( filepath, dtype=np.int16, delimiter=',')
    if not np.any(np.where( data == 1 )):
        return False, 'no ones'
    h,w = data.shape
    bites = QByteArray( data.tobytes() ) 
    block = QgsRasterBlock( Qgis.CInt16, w, h)
    block.setData( bites)
    if not block.isValid():
        return False, 'block invalid'
    fw = QgsRasterFileWriter(outpath)
    fw.setOutputFormat('gpkg')
    fw.setCreateOptions(['RASTER_TABLE='+layerName, 'APPEND_SUBDATASET=YES'])
    provider = fw.createOneBandRaster( Qgis.Int16, w, h, extent, crs )
    ''' mark zeros as nodata '''
    provider.setNoDataValue(1, 0)
    if not provider.isValid():
        return False, 'provider invalid'
    if not provider.isEditable():
        return False, 'provider not editable'
    if not provider.writeBlock( block, 1, 0, 0):
        return False, 'provider failed to write block'
    return True, 'sucess for'+layerName

import processing
from qgis.core import QgsVectorDataProvider, QgsField, QgsGeometry #, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant

from collections import namedtuple
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

def rasterpolygonize(layer, output=None):# ): #
    ''' processing.algorithmHelp('gdal:polygonize')
    { 'BAND' : 1, 'EIGHT_CONNECTEDNESS' : False, 'EXTRA' : '', 'FIELD' : 'DN', 'INPUT' : layer, 'OUTPUT' : 'TEMPORARY_OUTPUT' })
    '''
    tmp = processing.run('gdal:polygonize',{ 'BAND' : 1, 'EIGHT_CONNECTEDNESS' : False, 'EXTRA' : '', 'FIELD' : 'DN', 'INPUT' : layer, 'OUTPUT' : output })
    return tmp['OUTPUT']

def mergeVectorLayers(layerList, ogrDB, tableName):
    '''processing.algorithmHelp('native:mergevectorlayers') -> Merge vector layers
            { 'CRS' : None, 'LAYERS' : layerList, 'OUTPUT' : 'TEMPORARY_OUTPUT' })
            ['/home/.../FireEvolution.gpkg|layername=polygon_ForestGrid01','/home...FireEvolution.gpkg|layername=polygon_ForestGrid02', ...]
            'OUTPUT' : 'ogr:dbname=\'/home/.../FireEvolution.gpkg\' table=\"merged_polygons\" (geom) sql='
    '''
    tmp = processing.run('native:mergevectorlayers',
            { 'CRS' : None, 'LAYERS' : layerList, 'OUTPUT' : 'ogr:dbname=\''+ogrDB+'\' table=\"'+tableName+'\" (geom) sql=' })
    return tmp

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

def convertRasterToNumpyArray(lyr): #Input: QgsRasterLayer
    values=[]
    provider= lyr.dataProvider()
    block = provider.block(1,lyr.extent(),lyr.width(),lyr.height())
    for i in range(lyr.width()):
        for j in range(lyr.height()):
            values.append(block.value(i,j))
    return np.array(values)

from itertools import islice
def csv2ascList( file_list = ['ForestGrid00.csv','ForestGrid01.csv'], header_file = 'elev.asc' ):
    with open( header_file, 'r') as afile:
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
            outfile.write(infile.read().replace(b',',b' '))

# Qt
''' 
    matplotlib into qt
      fig,canvas from qt objects
      graphs using QGraphicsScene (multi figure manager) into a QGraphicsView (ui component)
    Work in progress only inserts single graph
    TODO accumulate figures inside the scene
    show next, previous 
'''
from qgis.PyQt.QtWidgets import QGraphicsScene, QGraphicsProxyWidget, QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
class MatplotlibModel(QGraphicsScene):
    def __init__(self, parent=None):
        super(MatplotlibModel, self).__init__(parent)
        self.static_canvas = None
        self.static_ax = None

    def newStaticFigCanvas(self, w=4, h=6):
        self.static_canvas = FigureCanvas(Figure(figsize=(w, h)))
        self.static_ax = self.static_canvas.figure.subplots()
        return self.static_canvas, self.static_ax

    def setGraphicsView(self, gv):
        #scene = QGraphicsScene() <-- scene is self!!
        proxy_widget = QGraphicsProxyWidget()
        widget = QWidget()
        layout = QVBoxLayout()
        #
        layout.addWidget(NavigationToolbar(self.static_canvas))
        layout.addWidget(self.static_canvas)
        #
        widget.setLayout(layout)
        proxy_widget.setWidget(widget)
        # insert widget into scene into view:
        self.addItem(proxy_widget)
        gv.setScene(self)
'''
    https://matplotlib.org/stable/api/figure_api.html
    class matplotlib.figure.Figure(figsize=None, dpi=None, *, facecolor=None, edgecolor=None, linewidth=0.0, frameon=None, subplotpars=None, tight_layout=None, constrained_layout=None, layout=None, **kwargs)
    ax          = canvas.figure.add_axes
    add_subplot
    subplots
    clf
'''
from qgis.PyQt.QtWidgets import QGraphicsScene, QGraphicsView, QComboBox, QWidget, QVBoxLayout, QGraphicsProxyWidget
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
class MatplotlibFigures(QGraphicsScene):
    def __init__(self, parent = None, graphicsView = None):
        super(MatplotlibFigures, self).__init__(parent)
        self.canvass = []
        self.proxy_widgets = []
        self.resize = []
        self.cv = -1
        self.graphicsView = graphicsView
        self.oldResizeEvent = self.graphicsView.resizeEvent
        self.graphicsView.resizeEvent = self.resizeEvent
        self.graphicsView.setScene(self)

    def resizeEvent(self, QResizeEvent):
        if self.cv == -1:
            return
        if not self.resize[self.cv]:
            return
        oldSize = QResizeEvent.oldSize()
        ow = oldSize.width()
        oh = oldSize.height()
        size = QResizeEvent.size()
        w = size.width()
        h = size.height()
        ds = abs(w-ow)+abs(h-oh)
        if ds < 4:
            return
        if ds < 8:
            self.fit2gv(self.cv)
            return
        self.proxy_widgets[self.cv].resize(w-5,h-5)
        self.oldResizeEvent( QResizeEvent)

    def new(self, w = None, h = None, **kwargs):
        if w and h:
            canvas = FigureCanvas( Figure( figsize=(w, h), **kwargs))
            self.resize += [ False ]
        else:
            canvas = FigureCanvas( Figure( **kwargs))
            self.resize += [ True ]
        proxy_widget = QGraphicsProxyWidget()
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget( NavigationToolbar(canvas))
        layout.addWidget( canvas)
        widget.setLayout( layout)
        proxy_widget.setWidget(widget)
        proxy_widget.setVisible(False)
        self.addItem(proxy_widget)
        self.canvass += [ canvas ]
        self.proxy_widgets += [ proxy_widget]
        return canvas

    def resize2gv(self, idx):
        w = self.graphicsView.size().width() - 5
        h = self.graphicsView.size().height() - 5
        self.proxy_widgets[idx].resize(w,h)

    def fit2gv(self, idx):
        self.graphicsView.fitInView( self.proxy_widgets[idx])

    def show(self, idx):
        if self.cv == idx:
            return
        if self.resize[idx]:
            self.resize2gv(idx)
        self.proxy_widgets[idx].setVisible(True)
        self.proxy_widgets[self.cv].setVisible(False)
        self.cv = idx


from qgis.PyQt.QtCore import Qt, QVariant, QAbstractTableModel
''' show pandas dataframe in qt '''
class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(str(self._data.iloc[index.row(), index.column()]))
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

''' Argparse '''
def get_params(Parser):
    ''' get an argparse object that has groups 
        args, parser, groups = get_params(Parser)

        from argparse import ArgumentParser
        parser = ArgumentParser()

    '''
    parser, groups = get_grouped_parser(Parser())
    args = { dest:parser[dest]['default'] for dest in parser.keys() }
    return args, parser, groups

def get_grouped_parser(parser):
    ''' groupObject = parser.add_argument_group(title='groupTitle to show')
        groupObject.add_argument("--le-argument", ...
        see usr/lib/python39/argparse.py for details
        groups are stored on _action_groups, lines: 1352, 1448
    '''
    pag = parser.__dict__['_action_groups']
    '''
        p[0]['title'] : 'positional' 
        p[1]['title'] : 'optional arguments'
        p[2:]['title'] : groups
    '''
    q = {}
    for p in pag[2:]:
        r = p.__dict__
        q[r['title']] = r['_group_actions']
    groups = set(q.keys())
    # normalize 
    args = {}
    for k,v in q.items():
        for w in v:
            x = w.__dict__
            args[x['dest']] = x  
            args[x['dest']].pop( 'container')
            args[x['dest']].update({ 'group' : k})

    return args, groups

import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)-8s %(message)s' ,datefmt='%Y-%m-%d %H:%M:%S')
#logging.basicConfig(level=logging.DEBUG)
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
from qgis.core import Qgis, QgsMessageLog
def log(*args, pre='', level=1, plugin=aName, msgBar=None):
    '''
    log(*args, level=1)

    logMessage(message: str, tag: str = '', level: Qgis.MessageLevel = Qgis.Warning, notifyUser: bool = True)
    
    import logging
    logging.warning('%s before you %s', 'Look', 'leap!')

    log = lambda m: QgsMessageLog.logMessage(m,'My Plugin') 
    log('My message')
          Qgis.[Info,   Warning, Critical,          Success]
    log.[debug, info,   warning, error and critical]
             0, 1   ,   2,          3               ,   4
    '''
    plugin = str(plugin)+' ' if plugin!='' else ''
    pre = str(pre)+' ' if pre!='' else ''
    
    if isinstance(args,tuple) and args!='':
        tmp = []
        for a in args:
            tmp += [str(a)]
        args = ' '.join(tmp)

    if level == 0:
        logging.debug( plugin+pre+args)
        QgsMessageLog.logMessage( 'debug '+pre+args, plugin, level=Qgis.Info) 
        if msgBar:
            msgBar.pushMessage( pre+'debug', args, level=Qgis.Info, duration=1)
    elif level == 1:
        QgsMessageLog.logMessage( pre+args, plugin, level=Qgis.Info) 
        logging.info( plugin+pre+args)
        if msgBar:
            msgBar.pushMessage( pre, args, level=Qgis.Info)
    elif level == 2:
        QgsMessageLog.logMessage( pre+args, plugin, level=Qgis.Warning) 
        logging.warning( plugin+pre+args)
        if msgBar:
            msgBar.pushMessage( pre, args, level=Qgis.Warning)
    elif level == 3:
        QgsMessageLog.logMessage( pre+args, plugin, level=Qgis.Critical) 
        logging.critical( plugin+pre+args)
        if msgBar:
            msgBar.pushMessage( pre, args, level=Qgis.Critical)
    elif level == 4:
        QgsMessageLog.logMessage( pre+args, plugin, level=Qgis.Success) 
        logging.info( plugin+'success '+pre+args)
        if msgBar:
            msgBar.pushMessage( pre, args, level=Qgis.Success)

def randomNames(n=8, l=4):
    ''' n words, l word length
    for i in range(20):
        for j in range(1,i):
           print(i,j,randomNames(i,j))
    '''
    m = n*l
    lis = map( chr, np.random.randint(97,123,size=m))
    joi = ''.join(lis)
    return [ joi[i:i+l] for i in range(0,m,l) ]

def randomDataFrame(rows=8, cols=4, dtype=float):
    if dtype == float:
        data = np.round( np.random.random(size=(rows,cols)) , 2)
    elif dtype == int:
        data =           np.random.randint(99, size=(rows,cols))
    else:
        raise NotImplementedError
    df = DataFrame( data, columns=randomNames(cols,3))
    df.insert( 0, randomNames(1,6)[0], Series(randomNames(rows,4)))
    return df

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def safe_cast_ok(val, to_type, default=None):
    try:
        return to_type(val), True
    except (ValueError, TypeError):
        return default, False

def check(obj,key):
    return hasattr(obj, key) and callable(getattr(obj, key))

if __name__ == "__main__":
    '''
    from qgis.core import QgsApplication, QgsProject
    from qgis.gui import QgsMapCanvas
    app = QgsApplication([], True)
    app.initQgis()
    canvas = QgsMapCanvas()
    project = QgsProject.instance()
    '''
    import sys
    from qgis.PyQt import QtWidgets
    app    = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    scene = QtWidgets.QScene()
    graphicsView = QtWidgets.QGraphicsView()

