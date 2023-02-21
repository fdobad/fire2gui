# -*- coding: utf-8 -*-
#REPLENV: /home/fdo/pyenv/qgis
"""
/***************************************************************************
 fire2amClass
                                 A QGIS plugin
 Simulate a forest fires under different weather and fire model scenarios
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-02-07
        git sha              : $Format:%H$
        copyright            : (C) 2023 by fdobadvel (gui) & fire2a team
        email                : fire2a@fire2a.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDoubleSpinBox, QSpinBox
from qgis.PyQt.QtTest import QTest
from qgis.PyQt.Qt import Qt
from qgis.core import QgsProject, Qgis, QgsWkbTypes, QgsMapLayerType, QgsFeatureRequest#, QgsMessageLog , QgsApplication, QgsTask

# Initialize Qt resources from file resources.py
from .img.resources import *
# Import the code for the dialog
from .fire2am_dialog import fire2amClassDialog
from .fire2am_argparse import fire2amClassDialogArgparse
from .fire2am_utils import (    randomDataFrame, MatplotlibModel, check, aName, log, 
                                getVectorLayerStuff, pixelstopolygons, addautoincrementalfield, add2dIndex , addXYcentroid, get_params)
from .ParseInputs import Parser

from pandas import DataFrame, read_csv
from datetime import datetime, timedelta
from multiprocessing import cpu_count
from shutil import copy
from glob import glob
import numpy as np
import os.path

#import pdb
#from qgis.PyQt.QtCore import pyqtRemoveInputHook
# These lines allow you to set a breakpoint in the app
#pyqtRemoveInputHook()
#pdb.set_trace()
# This line enters into interactive
#(Pdb) !import code; code.interact(local=vars())

# ?
#import warnings
#warnings.filterwarnings("ignore",message='Warning: QCoreApplication::exec: The event loop is already running')

class fire2amClass:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'fire2amClass_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Fire Simulator Analytics Management')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start_dialog = None
        self.first_start_argparse = None
        # global
        self.default_args, self.parser, self.groups = get_params(Parser)
        self.project = None
        self.layer = {}
        self.plt = MatplotlibModel()
        self.args = {}
        # timers
        self.timer_weatherFile = QTimer()
        self.timer_weatherFile.setSingleShot(True)
        self.timer_weatherFolder = QTimer()
        self.timer_weatherFolder.setSingleShot(True)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('fire2amClass', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/fire2am/img/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'%s: setup and run a forest fire simulation...'%aName),
            callback=self.run_Dialog,
            parent=self.iface.mainWindow())
        # dock start
        self.add_action(
            icon_path = ':/plugins/fire2am/img/icon_dev.png',
            text = self.tr(u'%s: all options (very experimental)'%aName),
            callback = self.run_Argparse,
            parent = self.iface.mainWindow(),
            add_to_toolbar = True)
        # dock end

        # will be set False in run()
        self.first_start_dialog = True
        self.first_start_argparse = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Fire Simulator Analytics Management'),
                action)
            self.iface.removeToolBarIcon(action)

    def run_Argparse(self):
        """Run method that performs all the real work"""
        if self.first_start_argparse == True:
            self.first_start_argparse = False
            self.argdlg = fire2amClassDialogArgparse()
        # show the dialog
        self.argdlg.show()
        # Run the dialog event loop
        result = self.argdlg.exec_()
        print('argdlg result',result)
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def run_Dialog(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start_dialog == True:
            self.first_start_dialog  = False
            self.dlg = fire2amClassDialog()
            # project
            self.project = QgsProject().instance()
            # connections
            self.dlg.button_box.clicked.connect(self.slot_button_box_clicked)
            self.dlg.tabWidget.currentChanged.connect(self.slot_tabWidget_currentChanged)
            self.dlg.tabWidget.setCurrentIndex(0)
            self.dlg.layerComboBox_fuels.layerChanged.connect( self.slot_layerComboBox_fuels_layerChanged)
            self.dlg.layerComboBox_elevation.layerChanged.connect( self.slot_layerComboBox_elevation_layerChanged)
            # folders
            self.dlg.fileWidget_weatherFile.setFilePath( self.project.absolutePath())
            self.dlg.fileWidget_weatherFolder.setFilePath( self.project.absolutePath())
            self.dlg.args['nweathers'] = 0
            # elevation fuels ignitions default names
            layers_byName = { l.name():l for l in QgsProject.instance().mapLayers().values()}
            if 'elevation' in layers_byName:
                self.dlg.layerComboBox_elevation.setLayer(layers_byName['elevation'])
            if 'fuels' in layers_byName:
                self.dlg.layerComboBox_fuels.setLayer(layers_byName['fuels'])
            if 'ignitions' in layers_byName:
                self.dlg.layerComboBox_ignitionPoints.setLayer(layers_byName['ignitions'])
            #
            self.dlg.msgBar.pushMessage(aName+' Hello World!','(Keep a project with layers open when interacting)', duration=-1, level=Qgis.Info)

        if QgsProject.instance().mapLayers() == {}:
            self.iface.messageBar().pushCritical(aName+': No layers found', 'Open a project with layers and try again')
            log('Open a project with layers and try again', pre='No layers found', level=3)
            return

        if self.project != QgsProject().instance():
            old = self.project
            self.project = QgsProject().instance()
            log( 'Old: %s %s New: %s %s'%( old.absoluteFilePath(), old.baseName(),
                                  self.project.absoluteFilePath(), self.project.baseName()), pre='Project Changed!', level=3, msgBar=self.dlg.msgBar)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        print('result',result)
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def processLayers(self):
        # TODO clip layers to study area instead of taking fuels as base
        log('processing layers',level=0)#, msgBar=self.dlg.msgBar)

        '''create a numerated cell grid BASED ON FUELS'''
        polyLayer = pixelstopolygons(self.dlg.state['layerComboBox_fuels'])
        polyLayer = addautoincrementalfield(polyLayer)
        addXYcentroid( polyLayer )
        add2dIndex( polyLayer, x='center_x', y='center_y')
        ''' add to project '''
        polyLayer.setName('instance_grid')
        polyLayer.loadNamedStyle(os.path.join( self.plugin_dir, 'img/instanceGrid_layerStyle.qml'))
        QgsProject.instance().addMapLayer(polyLayer)
        self.layer['grid'] = polyLayer

        ''' create ignition cells layer '''
        if self.dlg.state['radioButton_ignitionRandom'] or self.dlg.state['radioButton_ignitionPoints']:

            if self.dlg.state['radioButton_ignitionRandom']:
                polyLayer.select( np.random.randint( len(polyLayer)))

            elif self.dlg.state['radioButton_ignitionPoints']:
                ''' in which cell a ignition point belongs to '''
                ignitions = self.dlg.state['layerComboBox_ignitionPoints']
                for ig in ignitions.getFeatures():
                    for p in polyLayer.getFeatures():
                        if p.geometry().contains(ig.geometry()):
                            polyLayer.select(p.id())
            ''' new layer from selected cells '''
            ignition_cells = polyLayer.materialize(QgsFeatureRequest().setFilterFids(polyLayer.selectedFeatureIds()))
            ''' add to project '''
            ignition_cells.setName('ignition_cells')
            ignition_cells.loadNamedStyle(os.path.join( self.plugin_dir, 'img/ignitionCells_layerStyle.qml'))
            QgsProject.instance().addMapLayer(ignition_cells)
            self.layer['ignitionPoints'] = ignition_cells

        elif self.dlg.state['radioButton_ignitionProbMap']:
            log( 'Checks not implemented', pre='ignitionProbMap',level=0, msgBar=self.dlg.msgBar)

    def makeInstance(self):
        '''mkdir directory, TODO from:copy&paste files to:write layers as new files
        '''
        os.mkdir( self.args['InFolder'])
        log( self.args['InFolder'],pre='Created directory',level=0, msgBar=self.dlg.msgBar)
        '''
        elevation '''
        elayer = self.dlg.state['layerComboBox_elevation']
        copy( elayer.publicSource() , self.args['InFolder'])
        log( 'elevation copied', level=0, msgBar=self.dlg.msgBar)
        '''
        fuels'''
        flayer = self.dlg.state['layerComboBox_fuels']
        copy( flayer.publicSource() , self.args['InFolder'])
        log( 'fuels copied',level=0, msgBar=self.dlg.msgBar)
        '''
        weather'''
        if self.dlg.state['radioButton_weatherRandom']:
            ''' generate one Weather.csv
            other columns=['Instance','datetime','WS','WD','FireScenario'])
            '''
            nrows = self.dlg.state['spinBox_max_fire_periods']
            dt = [ self.now + timedelta(hours=i) for i in range(nrows)]
            ''' totally random '''
            WD = np.random.randint(0,359,nrows)
            WS = np.random.randint(1,200,nrows)
            ''' one random '''
            WD = [np.random.randint(0,359)]*nrows
            WS = [np.random.randint(1,200)]*nrows
            df = DataFrame( np.vstack((dt,WD,WS)).T, columns=['datetime','WD','WS'])
            df.to_csv( os.path.join( self.args['InFolder'],'Weather.csv'), header=True, index=False)
            log( 'speed:%s direction:%s'%(WS,WD), pre='Random Wind', level=4, msgBar=self.dlg.msgBar)
        elif self.dlg.state['radioButton_weatherConstant']:
            ''' read dial and slider to generate Weather.csv '''
            nrows = self.dlg.state['spinBox_max_fire_periods']
            dt = [ self.now + timedelta(hours=i) for i in range(nrows)]
            WD = [ self.dlg.state['spinBox_windDirection'] ] * nrows
            WS = [ self.dlg.state['spinBox_windSpeed'] ] * nrows
            df = DataFrame( np.vstack((dt,WD,WS)).T, columns=['datetime','WD','WS'])
            df.to_csv( os.path.join( self.args['InFolder'],'Weather.csv'), header=True, index=False)
            log( 'speed:%s direction:%s'%(WS,WD), pre='Constant Wind', level=4, msgBar=self.dlg.msgBar)
        elif self.dlg.state['radioButton_weatherFile']:
            ''' copy weather file '''
            copy( self.dlg.state['fileWidget_weatherFile'], self.args['InFolder'])
            log( 'weather file copied', level=0, msgBar=self.dlg.msgBar)
        elif self.dlg.state['radioButton_weatherFolder']:
            ''' copy weather folder '''
            dst = os.path.join( self.args['InFolder'],'Weather')
            for filename in glob(self.dlg.state['fileWidget_weatherFolder']):
                basename = os.path.basename(filename)
                if basename[:7] == 'Weather' and basename[-4:] == '.csv':
                    copy( filename , dst)
            log( 'weather folder copied', level=0, msgBar=self.dlg.msgBar)
        ''' ignitions '''
        if self.dlg.state['radioButton_ignitionRandom'] or self.dlg.state['radioButton_ignitionPoints']:
            ''' ignition points are cells, read index, write csv '''
            ic_stuff = getVectorLayerStuff( self.layer['ignitionPoints'])
            data = { 'Year':None, 'Ncell': np.int16( ic_stuff.attr[ :, ic_stuff.names.index('index')])}
            df = DataFrame.from_dict( data)
            df.fillna(1, inplace=True)
            df.to_csv( os.path.join( self.args['InFolder'],'Ignitions.csv'), header=True, index=False)
            log( 'written', pre='Ignition points', level=0, msgBar=self.dlg.msgBar)
        elif self.dlg.state['radioButton_ignitionProbMap']:
            ipm_layer = self.dlg.state['layerComboBox_ignitionProbMap']
            copy( ipm_layer.publicSource() , self.args['InFolder'])
            log( 'ignitionProbMap copied', level=0, msgBar=self.dlg.msgBar)

    def slot_tabWidget_currentChanged(self):
        ''' connect signals when tab is opened
        sender = self.dlg.sender()
        senderName = sender.objectName()
        QgsMessageLog.logMessage('tab_callback\tci:%s\tname:%s'%(ci,senderName), MESSAGE_CATEGORY, level = Qgis.Info)
        TBD track connections id
                self.conn_id[ci] += [ self.dlg.radioButton_ignitionPoints.clicked.connect(self.slot_ignitionPoints_clicked)]
                self.conn_id[ci] += [ self.dlg.layerComboBox_ignitionPoints.layerChanged.connect(self.slot_ignitionPoints_layerChanged)]
        '''
        ci = self.dlg.tabWidget.currentIndex()
        if ci == 0:
            self.dlg.layerComboBox_fuels.layerChanged.connect( self.slot_layerComboBox_fuels_layerChanged)
            self.dlg.layerComboBox_elevation.layerChanged.connect( self.slot_layerComboBox_elevation_layerChanged)
        elif ci == 1:
            self.dlg.fileWidget_weatherFolder.fileChanged.connect( self.slot_fileWidget_weatherFolder_fileChanged)
            self.dlg.fileWidget_weatherFile.fileChanged.connect( self.slot_fileWidget_weatherFile_fileChanged)
            self.dlg.radioButton_weatherFolder.clicked.connect( self.slot_radioButton_weatherFolder_clicked)
            self.dlg.radioButton_weatherFile.clicked.connect( self.slot_radioButton_weatherFile_clicked)
        elif ci == 2:
            self.dlg.radioButton_ignitionPoints.clicked.connect(self.slot_radioButton_ignitionPoints_clicked)
            self.dlg.layerComboBox_ignitionPoints.layerChanged.connect(self.slot_layerComboBox_ignitionPoints_layerChanged)
            #self.dlg.radioButton_ignitionProbMap.clicked.connect(self.slot_radioButton_ignitionProbMap_clicked)
            #self.dlg.layerComboBox_ignitionProbMap.layerChanged.connect(self.slot_layerComboBox_ignitionProbMap_layerChanged)
        elif ci == 5:
            self.dlg.toolButton_next.clicked.connect(self.slot_toolButton_next_clicked)
            self.dlg.toolButton_prev.clicked.connect(self.slot_toolButton_prev_clicked)

    def slot_layerComboBox_fuels_layerChanged(self, layer):
        try:
            if not layer.type() == QgsMapLayerType.RasterLayer:
                log( 'Fuel layer '+layer.name(), pre='Not Raster!' , level=2, msgBar=self.dlg.msgBar)
            else:
                log( 'Fuel layer '+layer.name(), pre='Is raster!' , level=4, msgBar=self.dlg.msgBar)
        except Exception as e:
            log(e, pre='Fuel layer exception!', level=3, msgBar=self.dlg.msgBar)

    def slot_layerComboBox_elevation_layerChanged(self, layer):
        try:
            if not layer.type() == QgsMapLayerType.RasterLayer:
                log( 'Elevation layer '+layer.name(), pre='Not Raster!', level=2, msgBar=self.dlg.msgBar)
            else:
                log( 'Elevation layer '+layer.name(), pre='Is raster!' , level=4, msgBar=self.dlg.msgBar)
        except Exception as e:
            log(e, pre='Elevation layer exception!', level=3, msgBar=self.dlg.msgBar)

    def slot_layerComboBox_ignitionProbMap_layerChanged(self, layer):
        try:
            if not layer.type() == QgsMapLayerType.RasterLayer:
                log( 'Ignition Probability Map layer '+layer.name(), pre='Not Raster!', level=2, msgBar=self.dlg.msgBar)
            else:
                log( 'Ignition Probability Map layer '+layer.name(), pre='Is raster!' , level=4, msgBar=self.dlg.msgBar)
                return
        except Exception as e:
            log(e, pre='Ignition Probability Map layer exception!', level=3, msgBar=self.dlg.msgBar)
        self.dlg.radioButton_ignitionRandom.setChecked(True)

    def slot_layerComboBox_ignitionPoints_layerChanged(self, layer):
        def warn_reject(msg):
            self.dlg.radioButton_ignitionRandom.setChecked(True)
            log( 'layer '+layer.name(), pre=msg, level=2,msgBar=self.dlg.msgBar)
        try:
            if not layer.type() == QgsMapLayerType.VectorLayer:
                warn_reject('Not vector!')
                return
            if not layer.wkbType() == QgsWkbTypes.Point:
                warn_reject('Not with Points!')
                return
            pts = [ f.geometry() for f in layer.getFeatures() \
                    if check( f, 'geometry') and \
                       f.geometry().wkbType() == QgsWkbTypes.Point]
            self.dlg.args['num_ignitions'] = pts
            if len(pts) == 0:
                warn_reject('0 points found!')
                return
            log( 'Read from %s layer'%layer.name(), pre='%s points'%len(pts), level=4, msgBar=self.dlg.msgBar)
            self.dlg.radioButton_ignitionPoints.setChecked(True)
        except Exception as e:
            log( e, pre='Ignition Point layer exception!', level=2, msgBar=self.dlg.msgBar)

    def slot_fileWidget_weatherFolder_fileChanged(self, directory):
        self.timer_weatherFile.stop()
        self.timer_weatherFolder.stop()
        def restore():
            self.dlg.fileWidget_weatherFolder.blockSignals(True)
            self.dlg.fileWidget_weatherFolder.setFilePath( self.project.absolutePath())
            self.dlg.fileWidget_weatherFolder.blockSignals(False)
            self.dlg.radioButton_weatherRandom.setChecked(True)
            self.dlg.args['nweathers'] = 0
        try:
            ''' count sequential Weather files '''
            i=1
            while os.path.isfile( os.path.join( directory, 'Weather'+str(i)+'.csv')):
                i+=1
            i-=1
            if i==0: 
                ''' restore '''
                log( 'Weather files must be a consecutive numbered sequence [1..N]', pre='No Weather[1..N].csv files', level=2, msgBar=self.dlg.msgBar)
                restore()
                return
            log(  'Found in %s'%directory, pre='Weathers[1..%s].csv'%i, level=4, msgBar=self.dlg.msgBar)
            self.dlg.radioButton_weatherFolder.setChecked(True)
            self.dlg.state['radioButton_weatherFolder'] = True
            self.dlg.state['fileWidget_weatherFolder'] = directory
            self.dlg.args['nweathers'] = i
        except Exception as e:
            log( e, pre='Weather Folder %s exception'%directory, level=2, msgBar=self.dlg.msgBar)
            restore()

    def slot_fileWidget_weatherFile_fileChanged(self, filepath):
        self.timer_weatherFile.stop()
        self.timer_weatherFolder.stop()
        ''' can restore after exception '''
        def restore():
            self.dlg.fileWidget_weatherFile.blockSignals(True)
            self.dlg.fileWidget_weatherFile.setFilePath( self.project.absolutePath())
            self.dlg.fileWidget_weatherFile.blockSignals(False)
            self.dlg.radioButton_weatherRandom.setChecked(True)
        try:
            df = read_csv( filepath)
            if 'WS' not in df.columns or 'WD' not in df.columns or len(df)==0:
                log(  os.path.basename(filepath)+' file does not contain them', pre='Missing WD or WS columns!', level=2, msgBar=self.dlg.msgBar)
                restore()
                return
            log( 'has WD & WS columns, %s hours (rows)'%len(df), pre=os.path.basename(filepath), level=4, msgBar=self.dlg.msgBar)
            self.dlg.radioButton_weatherFile.setChecked(True)
            self.dlg.state['radioButton_weatherFile'] = True
            self.dlg.state['fileWidget_weatherFile'] = filepath
        except Exception as e:
            log( e, pre='Single .csv file %s exception'%filepath, level=2, msgBar=self.dlg.msgBar)
            restore()

    def slot_radioButton_weatherFile_clicked(self):
        filepath = self.dlg.fileWidget_weatherFile.filePath()
        if self.dlg.state['fileWidget_weatherFile'] == filepath and filepath[:-3]=='csv' or filepath == None:
            return
        #self.timer_weatherFile.timeout.connect( lambda : self.slot_fileWidget_weatherFile_fileChanged(filepath))
        self.timer_weatherFile.timeout.connect( lambda : self.slot_fileWidget_weatherFile_fileChanged(self.dlg.fileWidget_weatherFile.filePath()))
        self.timer_weatherFile.start(5000)

    def slot_radioButton_weatherFolder_clicked(self):
        filepath = self.dlg.fileWidget_weatherFolder.filePath()
        if self.dlg.state['fileWidget_weatherFile'] == filepath and self.dlg.state['nweathers'] != 0 or filepath == None:
            return
        #self.timer_weatherFolder.timeout.connect( lambda : self.slot_fileWidget_weatherFolder_fileChanged(filepath))
        self.timer_weatherFolder.timeout.connect( lambda : self.slot_fileWidget_weatherFolder_fileChanged(self.dlg.fileWidget_weatherFolder.filePath()))
        self.timer_weatherFolder.start(5000)

    def slot_radioButton_ignitionPoints_clicked(self):
        try:
            layer = self.dlg.layerComboBox_ignitionPoints.currentLayer()
            if self.args['layer_ignition_points'] == layer:
                return
            if layer.type() != QgsMapLayerType.VectorLayer:
                QTest.qWait(2000)
            layer = self.dlg.layerComboBox_ignitionPoints.currentLayer()
            self.slot_layerComboBox_ignitionPoints_layerChanged(layer)
        except Exception as e:
            print('Exception' ,e)

    def slot_toolButton_next_clicked(self):
        print('next clicked')

    def slot_toolButton_prev_clicked(self):
        print('prev clicked')

    def makeArgs(self):
        ''' from self.args.copy()
            update dlg values from spinboxes
            update tab logic
                weathers
                ignitions
            update argparse dialog
        '''
        args = {}
        log( 'makeArgs 0 base',args, level=0)

        '''
        Get values for all Double|SpinBox dlg components'''
        args.update( { o.objectName()[o.objectName().index('_')+1:]: o.value() 
            for o in self.dlg.findChildren( (QDoubleSpinBox, QSpinBox), 
                                        options= Qt.FindChildrenRecursively)})
        ''' these are used on weather file generation on makeInstance '''
        args.pop('windDirection')
        args.pop('windSpeed')
        log( 'makeArgs 1 spinboxes',args, level=0)

        ''' dlg tab logic (radioButtons per tab widget)
        TODO confirmar logica
        weather logic '''
        if self.dlg.state['radioButton_weatherFolder']:
            args['WeatherOpt'] = 'rows'
        elif self.dlg.state['radioButton_weatherFile'] or \
             self.dlg.state['radioButton_weatherRandom'] or \
             self.dlg.state['radioButton_weatherConstant']:
            args['WeatherOpt'] = 'constant'
            args['nweathers'] = 1
        ''' ignition logic '''
        args['ignitions'] = True
        log( 'makeArgs 2 tablogic',args, level=0)

        ''' update argparse dialog
        dialog did ever open? '''
        now_str = self.now.strftime('%y-%m-%d_%H-%M-%S')
        if self.first_start_argparse:
            ''' never opened '''
            args['InFolder'] = os.path.join( self.project.absolutePath(), 'Instance'+now_str)
            args['OutFolder'] = os.path.join( args['InFolder'], 'results')
            args['nthreads'] = max(1, cpu_count()-2)
        else:
            ''' did opened '''
            args.update(self.argdlg.gen_args)
            ''' but didnt mention ioFolder '''
            if 'InFolder' not in self.argdlg.gen_args.keys():
                args['InFolder'] = os.path.join( self.project.absolutePath(), 'Instance'+now_str)
            if 'OutFolder' not in self.argdlg.gen_args.keys():
                args['OutFolder'] = os.path.join( args['InFolder'], 'results')
            if 'nthreads' not in self.argdlg.gen_args.keys():
                args['nthreads'] = max(1, cpu_count()-2)

        self.args = args
        log( 'makeArgs 2 argparse + corrections self', self.args, level=0)

    def slot_button_box_clicked(self, button):
        if button.text() == 'Reset':
            print('Reset')
            self.dlg.updateState()
            self.makeArgs()
        elif button.text() == 'Apply':
            print('Apply')
            self.dummyApply()
            self.run_Simulation()
        elif button.text() == 'Restore Defaults':
            print('Restore Defaults')
            if not self.first_start_dialog:
                self.first_start_dialog = True
                self.dlg.destroy()
            if not self.first_start_argparse:
                self.first_start_argparse= True
                self.argdlg.destroy()

    def run_Simulation(self):
        self.now = datetime.now()
        self.dlg.updateState()
        self.processLayers()
        self.makeArgs()
        self.makeInstance()

    def dummyApply(self):
        # data
        self.dlg.tableView_1.setModel(self.dlg.PandasModel(randomDataFrame(12,6,int)))
        self.dlg.tableView_2.setModel(self.dlg.PandasModel(randomDataFrame(12,3,float)))

        # plot
        static_canvas, static_ax = self.plt.newStaticFigCanvas(5,3)
        static_ax.set(xlabel='time (s)', ylabel='voltage (mV)',
               title='Static -- About as simple as it gets, folks')
        t = np.linspace(0, 10, 50)
        static_ax.plot(t, np.tan(t), ".")
        self.plt.setGraphicsView( self.dlg.graphicsView)
        '''
        pyqtRemoveInputHook()
        pdb.set_trace()
        #(Pdb) !import code; code.interact(local=vars())
        '''

