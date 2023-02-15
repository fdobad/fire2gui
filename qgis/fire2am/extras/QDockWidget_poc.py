import os
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
#import code
#code.interact(local=dict(globals(), **locals()))

class PocDock(QtWidgets.QDockWidget):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(PocDock, self).__init__(parent)

        vlayout = QtWidgets.QVBoxLayout()

        tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(2)
        for i in range(3):
            parent = QtWidgets.QTreeWidgetItem(tree)
            parent.setText(0, "Parent {}".format(i))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in range(5):
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "Child {}".format(x))
                child.setText(1, "Value = {}".format(5-x))
                child.setCheckState(0, Qt.Unchecked)
        vlayout.addWidget(tree)
        self.tree = tree

        self.text = QtWidgets.QTextBrowser()
        self.fm = self.text.fontMetrics()
        self.text.setMinimumHeight(self.fm.height())
        self.text.setMaximumHeight(4*self.fm.height())
        self.text.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.text.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        self.text.setPlainText('-------- hola -------')


        self.clipboard_checkBox = QtWidgets.QCheckBox('put generated command on system clipboard')

        vlayout.addWidget( self.tree)
        vlayout.addWidget( self.clipboard_checkBox)
        vlayout.addWidget( self.text)

        w = QtWidgets.QWidget()
        w.setLayout(vlayout)
        self.setWidget(w)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def init_Tree(self):
        tree = QtWidgets.QTreeWidget()
        tree.AdjustToContentsOnFirstShow
        tree.setHeaderLabels(['dest','option_strings[0]','default->args.dest=value','type','help'])
        tree.setColumnCount(5)
        for group in groups:
            parent = QtWidgets.QTreeWidgetItem(tree)
            parent.setText(0, group)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            parent.setExpanded(True)
            for key,val in parser.items():
                if val['group'] == group:
                    child = QtWidgets.QTreeWidgetItem(parent)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
                    child.setText(0, str(val['dest']             ))
                    child.setText(1, str(val['option_strings'][0]))
                    child.setText(3, str(val['type']))
                    child.setText(4, str(val['help']))
                    # 2
                    child.setCheckState(0, Qt.Unchecked)
                    if val['type'] is None:
                        if args[key]:
                            child.setCheckState(0, Qt.Checked)
                        else:
                            child.setCheckState(0, Qt.Unchecked)
                    child.setText(2, str(args[key]))
                    child.setHidden(False)
        tree.setItemDelegateForColumn(0,DisableEditorDelegate())
        return tree

if __name__ == '__main__':
    import sys
    app      = QtWidgets.QApplication(sys.argv)
    widget   = PocDock()
    widget.setWindowTitle("Auto Argparse App")
    if False:
        ''' widget exec '''
        widget.show()
    else:
        ''' window exec '''
        window = QtWidgets.QMainWindow()
        window.setCentralWidget(widget)
        window.setWindowTitle("Auto Argparse App")
        window.show()
    sys.exit(app.exec_())

    '''
    for group in groups:
        for key,val in args.items():
            if val['group'] == group:
                print(group,key,val['group'] )
    def slot(*args, **kwargs):
        print('slot_','args',args,'kwargs',kwargs,sep='\t')

    tree    = QtWidgets.QTreeWidget()
    getSelected = tree.currentItem()
    #print(str(sys._getframe().f_lineno),getSelected)
    if getSelected:
        print(getSelected.text(0),getSelected.text(2))
        if(getSelected.text(0) in pars.keys()):
            pars_values[getSelected.text(0)] = getSelected.text(2)

    print('N',ns)
    global args
    args[itemChanged.text(0)] = itemChanged.text(2)
    ns = Namespace(**args)
    print(itemChanged.text(0) ,itemChanged.text(2), ns, sep='\n')

    for k,v in pars.items():
        item = QtWidgets.QTreeWidgetItem(tree)
        print(v['dest'])
        item.setText(0,v['dest'])
        item.setText(1,v['option_strings'][0])
        item.setText(3,v['help'])
        item.setFlags( item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsTristate)

    for i in range(3):
        parent = QtWidgets.QTreeWidgetItem(tree)
        parent.setText(0, "Parent {}".format(i))
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for x in range(5):
            child = QtWidgets.QTreeWidgetItem(parent)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, "Child {}".format(x))
            child.setCheckState(0, Qt.Unchecked)

    dialog_button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Yes|QtWidgets.QDialogButtonBox.No)
    v_layout.addWidget(dialog_button_box )
    '''
