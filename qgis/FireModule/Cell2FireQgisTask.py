from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )

MESSAGE_CATEGORY = 'Cell2Fire'

# No Warnings
import warnings
warnings.filterwarnings("ignore")
# Inputs and environment generator
# TODO : modify ParseInputs to not pickle from .ParseInputs import ParseInputs
from .Cell2FireC_class import *

import sys, os
from platform import system
# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
    if system() == 'Windows':
        sys.stderr = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__
    if system() == 'Windows':
        sys.stderr = sys.__stderr__

class Cell2FireTask(QgsTask):
    """This shows how to subclass QgsTask"""
    def __init__(self, args, description):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.args = args
        self.description = description
        self.path = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them internally and raise them in self.finished
        """
        try:
            QgsMessageLog.logMessage( 'Task "{}" run method started'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
            blockPrint()
            self.setProgress(0.0)
            if self.isCanceled():
                return False
            # c++ simulation
            QgsMessageLog.logMessage( 'Task "{}" c++ fire simulation started'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
            env = Cell2FireC(self.args)
            QgsMessageLog.logMessage( 'Task "{}" c++ fire simulation ended'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
            self.setProgress(33.0)
            if self.isCanceled():
                return False
            # Postprocessing: Plots Stats
            if self.args.stats:
                QgsMessageLog.logMessage( 'Task "{}" generating plots & statistics started'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
                env.stats()
                QgsMessageLog.logMessage( 'Task "{}" generating plots & statistics ended'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
            self.setProgress(66.0)
            if self.isCanceled():
                return False
            # heuristics
            if self.args.heuristic != -1:
                QgsMessageLog.logMessage( 'Task "{}" generating generating outputs for heuristics started'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
                env.heur()
                QgsMessageLog.logMessage( 'Task "{}" generating generating outputs for heuristics ended'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
            enablePrint()
        except Exception as e:
            self.exception = e
            return False
        QgsMessageLog.logMessage( 'Task "{}" run method ended'.format( self.description), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def finished(self, result):
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

    def cancel(self):
        super().cancel()
        QgsMessageLog.logMessage(
            'Task "{name}" cancel signal handled ok'.format(
            name=self.description),
            MESSAGE_CATEGORY, Qgis.Info)

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
