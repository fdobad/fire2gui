from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )

MESSAGE_CATEGORY = 'Cell2Fire'

# No Warnings
import warnings
warnings.filterwarnings("ignore")
# Inputs and environment generator
#from .ParseInputs import ParseInputs
from .Cell2FireC_class import *
#from .Stats import *
#from .Heuristics import *

import sys, os
# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

class Cell2FireTask(QgsTask):
    """This shows how to subclass QgsTask"""
    def __init__(self, args, description):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.args = args
        self.description = description
        QgsMessageLog.logMessage('__init__ task "{}"'.format(
                                     self.description),
                                 MESSAGE_CATEGORY, Qgis.Info)
        self.path = os.path.dirname(os.path.abspath(__file__))
        QgsMessageLog.logMessage('Path:' + self.path,
                                 MESSAGE_CATEGORY, Qgis.Info)

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them internally and raise them in self.finished
        """
        blockPrint()
        self.setProgress(0.0)
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if self.isCanceled():
            return False
        QgsMessageLog.logMessage('C++ init', MESSAGE_CATEGORY, Qgis.Info)
        env = Cell2FireC(self.args)
        QgsMessageLog.logMessage('C++ ran', MESSAGE_CATEGORY, Qgis.Info)
        #
        self.setProgress(33.0)
        if self.isCanceled():
            return False
        # Postprocessing: Plots Stats
        if self.args.stats:
            QgsMessageLog.logMessage('Generating Statistics', MESSAGE_CATEGORY, Qgis.Info)
            env.stats()
        #
        self.setProgress(66.0)
        if self.isCanceled():
            return False
        if self.args.heuristic != -1:
            QgsMessageLog.logMessage('Generating outputs for heuristics', MESSAGE_CATEGORY, Qgis.Info)
            env.heur()
        self.setProgress(100.0)
        return True

    def finished(self, result):
        QgsMessageLog.logMessage(
                'finished',
                MESSAGE_CATEGORY, Qgis.Success)
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed'.format(
                name=self.description),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without '\
                    'exception (probably the task was manually '\
                    'canceled by the user)'.format(
                    name=self.description),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage('Task "{name}" Exception: {exception}'.format(
                        name=self.description,
                        exception=self.exception),
                        MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception
        enablePrint()

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was canceled'.format(
            name=self.description),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()

if __name__ == '__main__':
    app = QgsApplication([], True)
    # On Linux, didn't need to set it so commented
    # app.setPrefixPath("C:/Program Files/QGIS Brighton/apps/qgis", True)
    app.initQgis()

    longtask = RandomIntegerSumTask('waste cpu long', 20)
    shorttask = RandomIntegerSumTask('waste cpu short', 10)
    minitask = RandomIntegerSumTask('waste cpu mini', 5)
    shortsubtask = RandomIntegerSumTask('waste cpu subtask short', 5)
    longsubtask = RandomIntegerSumTask('waste cpu subtask long', 10)
    shortestsubtask = RandomIntegerSumTask('waste cpu subtask shortest', 4)

    # Add a subtask (shortsubtask) to shorttask that must run after
    # minitask and longtask has finished
    shorttask.addSubTask(shortsubtask, [minitask, longtask])
    # Add a subtask (longsubtask) to longtask that must be run
    # before the parent task
    longtask.addSubTask(longsubtask, [], QgsTask.ParentDependsOnSubTask)
    # Add a subtask (shortestsubtask) to longtask
    longtask.addSubTask(shortestsubtask)

    QgsApplication.taskManager().addTask(longtask)
    QgsApplication.taskManager().addTask(shorttask)
    QgsApplication.taskManager().addTask(minitask)

    QgsApplication.exitQgis()
