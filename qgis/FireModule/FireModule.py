#REPLENV: /home/fdo/pyenv/qgis
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FireClass
                                 A QGIS plugin
 FireDescription
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-01-14
        git sha              : $Format:%H$
        copyright            : (C) 2023 by fdo bad vel
        email                : fernandobadilla@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsMessageLog, Qgis, QgsProject, QgsApplication, QgsTask
from qgis.gui import QgsMessageBar


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .FireModule_dialog import FireClassDialog
import os.path

# Use pdb for debugging
#import pdb
#from qgis.PyQt.QtCore import pyqtRemoveInputHook
# These lines allow you to set a breakpoint in the app
#pyqtRemoveInputHook()
#pdb.set_trace()

#from .C2FSB.Cell2FireQgisTask import Cell2FireTask
from .Cell2FireQgisTask import *
from argparse import Namespace
import pickle
from datetime import datetime
from pandas import DataFrame
import pyperclip

MESSAGE_CATEGORY = 'Cell2Fire'

class FireClass:
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
            'FireClass_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FireName')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        #
        # store cell2fire args
        self.args = {}
        self.pars = pickle.load(open(self.plugin_dir+'/pars.p','rb'))
        self.task = None
        self.taskManager = QgsApplication.taskManager()

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
        return QCoreApplication.translate('FireClass', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag = True,
        add_to_menu = True,
        add_to_toolbar = True,
        status_tip = None,
        whats_this = None,
        parent = None):
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
        icon_path = ':/plugins/FireModule/Fire.png'
        self.add_action(
            icon_path,
            text = self.tr(u'FireMenuItemText'),
            callback = self.run,
            parent = self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&FireName'),
                action)
            self.iface.removeToolBarIcon(action)

    def tab_callback(self):
        '''
        sender = self.dlg.sender()
        senderName = sender.objectName()
        QgsMessageLog.logMessage('tab_callback\tci:%s\tname:%s'%(ci,senderName), MESSAGE_CATEGORY, level = Qgis.Info)
        '''
        ci = self.dlg.tabWidget.currentIndex()
        if ci == 0:
            self.dlg.bar.pushMessage("FireGui", "Select a input folder to (re)scan for files", level = Qgis.Info)
        if ci == 5:
            pass
        if ci == 8:
            self.dlg.bar.pushMessage("FireGui", "stats->grids, [Any]plots->messages", level = Qgis.Info)
        if ci == 9:
            self.getParams()

    def file_callback(self):
        sender = self.dlg.sender()
        senderName = sender.objectName()
        filePath = sender.filePath()
        QgsMessageLog.logMessage('file picker name:%s\tchoosen:%s'%(senderName, filePath), MESSAGE_CATEGORY, level = Qgis.Info)
        #
        # logica ui
        if senderName == 'mQgsFileWidget_InFolder':
            # store
            self.args['InFolder'] = filePath
            if self.args['InFolder'][-1] != os.sep:
                self.args['InFolder'] = self.args['InFolder'] + os.sep
            # ignitions
            file_name='Ignitions.csv'
            if os.path.isfile( os.path.join( filePath, file_name)):
                self.dlg.mQgsFileWidget_Ignitions.setFilePath( os.path.join( filePath, file_name))
                self.dlg.radioButton_IgPointFile.click()
            else:
                self.dlg.mQgsFileWidget_Ignitions.lineEdit().setValue( file_name+' not found in input folder!')
            # py
            file_name='py.asc'
            if os.path.isfile( os.path.join( filePath, file_name)):
                self.dlg.mQgsFileWidget_IgProbMap.setFilePath( os.path.join( filePath, file_name))
                #self.dlg.radioButton_IgProbMapFile.click()
            else:
                self.dlg.mQgsFileWidget_IgProbMap.lineEdit().setValue( file_name+' not found in input folder!')
            # elevation
            file_name='elevation.asc'
            if os.path.isfile( os.path.join( filePath, file_name)):
                self.dlg.mQgsFileWidget_elevation.setFilePath( os.path.join( filePath, file_name))
                self.dlg.radioButton_elevationFile.click()
            else:
                self.dlg.mQgsFileWidget_elevation.lineEdit().setValue( file_name+' not found in input folder!')
            # fuels
            ## forest or fuels
            fo = os.path.isfile( os.path.join( filePath, 'Forest.asc'))
            fu = os.path.isfile( os.path.join( filePath, 'fuels.asc'))
            if fo or fu:
                if fu:
                    fn = 'fuels.asc'
                if fo:
                    fn = 'Forest.asc'
                self.dlg.mQgsFileWidget_Fuels.setFilePath( os.path.join( filePath, fn))
            else:
                self.dlg.mQgsFileWidget_Fuels.lineEdit().setValue("Neither Forest nor fuels (.asc) found in input folder!" )
            ## BBO
            file_name='BBOFuels.csv'
            if os.path.isfile( os.path.join( filePath, file_name)):
                self.dlg.mQgsFileWidget_BBO.setFilePath( os.path.join( filePath, file_name))
                self.dlg.checkBox_BBO.click()
            else:
                self.dlg.mQgsFileWidget_BBO.lineEdit().setValue( file_name+" not found in input folder!" )
            ## Treatment
            file_name='Harvest.csv'
            if os.path.isfile( os.path.join( filePath, file_name)):
                self.dlg.mQgsFileWidget_HCells.setFilePath( os.path.join( filePath, file_name))
                self.dlg.checkBox_HCells.click()
            else:
                self.dlg.mQgsFileWidget_HCells.lineEdit().setValue( file_name+" not found in input folder!" )
            ## Weather
            ### file
            file_name='Weather.csv'
            if os.path.isfile( os.path.join( filePath, file_name)):
                self.dlg.bar.pushMessage('FireGui', 'Weather.csv found!', level = Qgis.Info )
                self.dlg.radioButton_weather_rows.click()
                self.dlg.radioButton_weather_rows.setEnabled(True)
                wf=True
            else:
                self.dlg.bar.pushMessage('FireGui', 'No Weather.csv found!', level = Qgis.Info )
                self.dlg.radioButton_weather_rows.setDisabled(True)
                wf=False
            ### directory
            directory = os.path.join( filePath, 'Weathers/')
            if os.path.isdir( directory):
                i=1
                while os.path.isfile( os.path.join( directory, 'Weather'+str(i)+'.csv')):
                    i+=1
                i-=1
                if i==0:
                    self.dlg.bar.pushMessage('FireGui', 'Weathers folder found! But without Weather<N>.csv files!', level = Qgis.Warning, duration=2)
                    self.dlg.mQgsSpinBox_nweathers.setDisabled(True)
                    wd=True
                else:
                    self.dlg.bar.pushMessage('FireGui', 'Weathers folder found! '+str(i)+' available Weathers', level = Qgis.Info )
                    self.dlg.mQgsSpinBox_nweathers.setEnabled(True)
                    self.dlg.mQgsSpinBox_nweathers.setMaximum(i)
                    self.dlg.mQgsSpinBox_nweathers.setValue(i)
                    self.dlg.radioButton_RandW.click()
                    wd=False
            else:
                self.dlg.mQgsSpinBox_nweathers.setDisabled(True)
                self.dlg.bar.pushMessage('FireGui', 'Weathers folder not found!', level = Qgis.Info)
                wd=False
            if not wf and not wd:
                self.dlg.radioButton_ConstW.click()

    def getParams(self):
        '''
        # TODO modify parse args to not pickle it!
        # To get parsing options, in a ipython session:
        from argparse import ArgumentParser
        # Manually paste ParseInputs content from Cell2Fire/ParseInputs.py
        opac = parser._get_optional_actions()
        pars = { sa.dest : { 'optstr' : sa.option_strings[0], 'type': sa.type, 'default': sa.default} for sa in opac[1:] }
        import pickle
        pickle.dump(pars, open('pars.p','wb'))
        # add it to init
        self.pars = pickle.load('pars.p')
        '''
        self.args['InFolder'] = self.dlg.mQgsFileWidget_InFolder.filePath()
        if self.args['InFolder'][-1] != os.sep:
            self.args['InFolder'] = self.args['InFolder'] + os.sep
        self.args['OutFolder'] = self.dlg.mQgsFileWidget_OutFolder.filePath()
        self.args['sim_years'] = 1
        self.args['nsims'] = self.dlg.mQgsSpinBox_nsims.value()
        self.args['seed'] = self.dlg.mQgsSpinBox_seed.value()
        self.args['nthreads'] = self.dlg.mQgsSpinBox_nthreads.value()
        self.args['max_fire_periods'] = self.dlg.mQgsSpinBox_max_fire_periods.value()
        self.args['gridsStep'] = self.dlg.mQgsSpinBox_gridsStep.value()
        self.args['gridsFreq'] = self.dlg.mQgsSpinBox_gridsFreq.value()
        self.args['heuristic'] = -1
        self.args['messages_path'] = None
        self.args['GASelection'] = False
        if self.dlg.checkBox_HCells.isChecked() and self.dlg.mQgsFileWidget_HCells.filePath()!='':
            self.args['HCells'] = self.dlg.mQgsFileWidget_HCells.filePath()
        else:
            self.args['HCells'] = None
        self.args['msgHeur'] = ''
        self.args['planPath'] = ''
        self.args['TFraction'] = 1.0
        self.args['GPTree'] = False
        self.args['valueFile'] = None
        self.args['noEvaluation'] = False
        self.args['ngen'] = 500
        self.args['npop'] = 100
        self.args['tSize'] = 3
        self.args['cxpb'] = 0.8
        self.args['mutpb'] = 0.2
        self.args['indpb'] = 0.5
        if self.dlg.radioButton_weather_rows.isChecked():
            self.args['WeatherOpt'] = 'rows'
            self.args['nweathers'] = 1
        elif self.dlg.radioButton_RandW.isChecked():
            self.args['WeatherOpt'] = 'random'
            self.args['nweathers'] = self.dlg.mQgsSpinBox_nweathers.value()
        self.args['spreadPlots'] = self.dlg.checkBox_spreadPlots.isChecked() #False
        self.args['finalGrid'] = self.dlg.checkBox_finalGrid.isChecked() #False
        self.args['verbose'] = self.dlg.checkBox_verbose.isChecked() #False
        if self.dlg.radioButton_IgRandom.isChecked():
            self.args['ignitions'] = False
            self.args['IgRadius'] = 0
        elif self.dlg.radioButton_IgPointFile.isChecked():
            self.args['ignitions'] = True
            self.args['IgRadius'] = self.dlg.mQgsSpinBox_IgRadius.value()
        elif self.dlg.radioButton_IgPointLayer.isChecked():
            QgsMessageLog.logMessage('IgPointLayer NotImplemented', MESSAGE_CATEGORY, level = Qgis.Warning)
            # TODO layer to csv ?
            #self.args['IgRadius'] = self.dlg.mQgsSpinBox_IgRadius.value()
        else:
            QgsMessageLog.logMessage('WTF! line 283', MESSAGE_CATEGORY, level = Qgis.Critical)
        self.args['grids'] = self.dlg.checkBox_grids.isChecked() #False
        self.args['plots'] = self.dlg.checkBox_plots.isChecked() #False
        self.args['allPlots'] = self.dlg.checkBox_allPlots.isChecked() #False
        self.args['combine'] = self.dlg.checkBox_combine.isChecked() #False
        self.args['input_gendata'] = self.dlg.checkBox_input_gendata.isChecked() #False
        self.args['OutMessages'] = self.dlg.checkBox_OutMessages.isChecked() #False
        self.args['OutBehavior'] = self.dlg.checkBox_OutBehavior.isChecked() #False
        self.args['stats'] = self.dlg.checkBox_stats.isChecked() #False
        self.args['Geotiffs'] = self.dlg.checkBox_Geotiffs.isChecked() #False
        self.args['tCorrected'] = self.dlg.checkBox_tCorrected.isChecked() #False
        self.args['onlyProcessing'] = self.dlg.checkBox_onlyProcessing.isChecked() #False
        # TODO : BBO or BBOTunning ?
        self.args['BBO'] = self.dlg.checkBox_BBO.isChecked() #False
        self.args['cros'] = self.dlg.checkBox_cros.isChecked() #False
        self.args['fdemand'] = False
        self.args['pdfOutputs'] = self.dlg.checkBox_pdfOutputs.isChecked() #False
        self.args['input_PeriodLen'] = self.dlg.mQgsDoubleSpinBox_input_PeriodLen.value() #60
        self.args['weather_period_len'] = self.dlg.mQgsSpinBox_weather_period_len.value() #60
        self.args['ROS_Threshold'] = self.dlg.mQgsDoubleSpinBox_ROS_Threshold.value() #0.1
        self.args['HFI_Threshold'] = self.dlg.mQgsDoubleSpinBox_HFI_Threshold.value() #0.1
        self.args['ROS_CV'] = self.dlg.mQgsDoubleSpinBox_ROS_CV.value() #0.0
        self.args['HFactor'] = self.dlg.mQgsDoubleSpinBox_HFactor.value() #1.0
        self.args['FFactor'] = self.dlg.mQgsDoubleSpinBox_FFactor.value() #1.0
        self.args['BFactor'] = self.dlg.mQgsDoubleSpinBox_BFactor.value() #1.0
        self.args['EFactor'] = self.dlg.mQgsDoubleSpinBox_EFactor.value() #1.0
        self.args['ROS10Factor'] = self.dlg.mQgsDoubleSpinBox_ROS10Factor.value() #3.34
        self.args['CCFFactor'] = self.dlg.mQgsDoubleSpinBox_CCFFactor.value() #0.0
        self.args['CBDFactor'] = self.dlg.mQgsDoubleSpinBox_CBDFactor.value() #0.0
        # todo : cmd better logic (e.g. if cros is false don't put CCFFactor)
        cmd='python main.py '
        for k,v in self.args.items():
            if isinstance(self.args[k], bool):
                if self.args[k]:
                    cmd += self.pars[k]['optstr'] + ' '
                else:
                    pass
            elif self.args[k] == '' or self.args[k] == None:
                pass
            else:
                cmd += self.pars[k]['optstr'] + ' ' + str(self.args[k]) + ' '
        #
        ns = Namespace(**self.args)
        #QgsMessageLog.logMessage('args dictionary\t%s'%(self.args), MESSAGE_CATEGORY, level = Qgis.Info)
        QgsMessageLog.logMessage('args Namespace\t%s'%(ns), MESSAGE_CATEGORY, level = Qgis.Info)
        #QgsMessageLog.logMessage('args cmd\t%s'%(cmd), MESSAGE_CATEGORY, level = Qgis.Info)
        self.dlg.textBrowser.setText('python main.py %s'%(cmd))
        #
        if self.dlg.checkBox_clipboard.isChecked():
            pyperclip.copy(cmd)
        return ns

    def runCell2Fire(self):
        if self.task is None or (isinstance( self.task, QgsTask) and self.task.status()==4):
            argsNs = self.getParams()
            fn = os.path.basename( QgsProject.instance().fileName())
            self.task = Cell2FireTask(argsNs , fn if fn!='' else 'no project open')
            self.taskManager.addTask(self.task)
        else:
            QgsMessageLog.logMessage('Task already running!, with status %s'%self.task.status(), MESSAGE_CATEGORY, level = Qgis.Info)

    def cancelCell2Fire(self):
        if self.task is None:
            return
        if self.task.canCancel():
            self.task.cancel()
            return
        QgsMessageLog.logMessage('Cannot cancel', MESSAGE_CATEGORY, level = Qgis.Critical)

    def cancelAll(self):
        if self.task is None:
            return
        self.taskManager.cancelAll()
        QgsMessageLog.logMessage('All tasks cancel signal emmited!', MESSAGE_CATEGORY, level = Qgis.Critical)

    def doConstantWeather(self):
        ''' ask and overwrite weather.csv
        '''
        if os.path.isfile( os.path.join( self.args['InFolder'], 'Weather.csv')):
            self.dlg.bar.pushMessage('FireGui', 'Weather.csv already exists!', level = Qgis.Warning)
            question = QMessageBox.question( self.dlg, 'Irreversible!', 'Overwrite Weather.csv?')
            if question != QMessageBox.Yes:
                self.dlg.bar.pushMessage('FireGui', 'Canceled', level = Qgis.Info)
                return
        ws = self.dlg.spinBox_ConstWS.value()
        wd = self.dlg.spinBox_ConstWD.value()
        #QgsMessageLog.logMessage("doConstantWeather\tws:%s\twd:%s"%(ws,wd), MESSAGE_CATEGORY, level = Qgis.Info)
        # TODO : headers ok? version canada?
        df = DataFrame( columns=['Instance','datetime','WS','WD','FireScenario'])
        df.loc[len(df)] = ['guiGeneratedInstance',datetime.now(),ws,wd,1]
        df.to_csv( os.path.join( self.args['InFolder'],'Weather.csv'), header=True, index=False)
        self.dlg.radioButton_weather_rows.setEnabled(True)
        self.dlg.radioButton_weather_rows.click()
        self.dlg.bar.pushMessage('FireGui', 'Weather.csv written', level = Qgis.Success)

    def clipboardChecked(self):
        # TODO when you disable it still get's ran one more time
        self.getParams()

    def run(self):
        """Run method that performs all the real work"""
        # Get the project instance
        project = QgsProject.instance()
        projectDir = project.homePath()
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = FireClassDialog()
            #
            # message level : Info, Warning, Critical or Success
            # duration : 0=forever, -1=level default
            self.dlg.bar = QgsMessageBar()
            self.dlg.layout().insertRow(0,self.dlg.bar) # at the end: .addRow . see qformlayout
            self.dlg.bar.pushMessage("I'm FireGui", "Hello World! Select a input folder to scan for files", level = Qgis.Info, duration = 0)
            #
            # object.signal.connect(slot)
            # tabs
            self.dlg.tabWidget.currentChanged.connect(self.tab_callback)
            # folders
            ## in
            self.dlg.mQgsFileWidget_InFolder.setFilePath( projectDir)
            if True:
                if system()=='Windows':
                    self.dlg.mQgsFileWidget_InFolder.setFilePath( 'C:/Users/fdo/Source/repos/cell2fire/data/')
                elif system()=='Linux':
                    self.dlg.mQgsFileWidget_InFolder.setFilePath( '/home/fdo/source/Cell2Fire/data/')
            self.dlg.mQgsFileWidget_InFolder.fileChanged.connect( self.file_callback)
            ## out
            self.dlg.mQgsFileWidget_OutFolder.setFilePath( projectDir)
            self.dlg.mQgsFileWidget_OutFolder.fileChanged.connect( self.file_callback)
            # run
            self.dlg.pushButton_Run.clicked.connect(self.runCell2Fire)
            self.dlg.pushButton_Cancel.clicked.connect(self.cancelCell2Fire)
            self.dlg.pushButton_CancelAll.clicked.connect(self.cancelAll)
            self.dlg.checkBox_clipboard.toggled.connect( self.clipboardChecked)
            # weather
            self.dlg.pushButton_writeWeather.clicked.connect(self.doConstantWeather)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            QgsMessageLog.logMessage('plugin main run result True', MESSAGE_CATEGORY, level = Qgis.Info)
        else:
            QgsMessageLog.logMessage('plugin main run result False', MESSAGE_CATEGORY, level = Qgis.Info)
