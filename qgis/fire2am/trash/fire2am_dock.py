#!/usr/bin/env python3
#NOREPLENV: /home/fdo/pyvenv/qgis
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys, pickle
from argparse import Namespace
from .ParseInputs import Parser
import pyperclip
from .fire2am_utils import safe_cast_ok, aName
from PyQt5.QtCore import pyqtSignal, Qt

def get_params():
    parser, groups = get_grouped_parser(Parser())
    args = { dest:parser[dest]['default'] for dest in parser.keys() }
    return args, parser, groups

def get_grouped_parser(parser):
    '''see usr/lib/python39/argparse.py for details
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


def makeSizePolicy():
    '''
        policies       Expanding Fixed Ignored Maximum Minimum MinimumExpanding Preferred
        pol Flag   ExpandFlag GrowFlag IgnoreFlag ShrinkFlag       
    '''
    sizePolicy = QtWidgets.QSizePolicy()
    pol = QtWidgets.QSizePolicy.Policy.Expanding 
    fla = QtWidgets.QSizePolicy.PolicyFlag.ExpandFlag 
    sizePolicy.setHorizontalPolicy( pol)
    sizePolicy.setVerticalPolicy( pol)
    sizePolicy.setHorizontalStretch(9999999)
    sizePolicy.setVerticalStretch(9999999)
    sizePolicy.setHeightForWidth(True)
    sizePolicy.setControlType( QtWidgets.QSizePolicy.ControlType.Frame )
    return sizePolicy

class fire2amClassDock(QtWidgets.QDockWidget):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(fire2amClassDock, self).__init__(parent)
        self.args, self.parser, self.groups = get_params()
        print(self.args, self.groups)
        self.setupUi()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def setupUi(self):
        self.setWindowTitle(aName +' all options (very experimental)')
        # add stuff to a layout
        vlayout = QtWidgets.QVBoxLayout()
        # tree
        tree = self.init_Tree()
        vlayout.addWidget(tree)
        self.tree = tree
        vlayout.addWidget( self.tree, stretch=10)
        # text browser
        text = QtWidgets.QTextBrowser()
        fm = text.fontMetrics()
        text.setMinimumHeight(fm.height())
        text.setMaximumHeight(4*fm.height())
        #text.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents)
        #text.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        #text.setBaseSize(10000,10000)
        text.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        text.setVisible(False)
        vlayout.addWidget(text)
        self.text = text
        # buttons
        hlayout = QtWidgets.QHBoxLayout()
        self.button_load = QtWidgets.QPushButton( self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton), 'Load')
        self.button_save = QtWidgets.QPushButton( self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton), 'Save')
        self.button_toggle = QtWidgets.QPushButton( self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowDown), '')
        self.state_visible = False
        self.button_toggle.clicked.connect( self.slot_button_toggle_clicked)
        hlayout.addWidget( self.button_load)
        hlayout.addWidget( self.button_save)
        hlayout.addWidget( self.button_toggle)
        vlayout.addLayout( hlayout)
        # end
        w = QtWidgets.QWidget()
        w.setLayout(vlayout)
        self.setWidget(w)

    def slot_button_toggle_clicked(self):
        if self.state_visible:
            print('True!')
            self.button_toggle.setIcon( self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowDown))
            self.text.setVisible(False)
            self.state_visible = False
        else:
            print('False!')
            self.button_toggle.setIcon( self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowUp))
            self.text.setVisible(True)
            self.state_visible = True

    def init_Tree(self):
        tree = QtWidgets.QTreeWidget()
        tree.setHeaderLabels(['dest','option_strings[0]','default->args.dest=value','type','help'])
        tree.setColumnCount(5)
        for group in self.groups:
            parent = QtWidgets.QTreeWidgetItem(tree)
            parent.setText(0, group)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            parent.setExpanded(True)
            for key,val in self.parser.items():
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
                        if self.args[key]:
                            child.setCheckState(0, Qt.Checked)
                        else:
                            child.setCheckState(0, Qt.Unchecked)
                    child.setText(2, str(self.args[key]))
                    child.setHidden(False)
        tree.setItemDelegateForColumn(0,DisableEditorDelegate())
        #tree.AdjustToContentsOnFirstShow
        #tree.setSizePolicy( makeSizePolicy())
        #tree.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        #tree.setBaseSize(1000,1000)
        #tree.setMinimumHeight(600)
        #tree.setMaximumHeight(2000)
        #tree.setWindowFlag(QtWidgets.QSizePolicy.PolicyFlag.ExpandFlag)
        #tree.setSizePolicy( QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        #tree.setSizePolicy( QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        #tree.updateGeometry()
        return tree

'''
def get_args(parser):
    parser = { a.dest : a.__dict__ for a in Parser()._get_optional_actions() }
    parser.pop('help')
    #metavars = set( v['metavar'] for k,v in parser.items())
    args = { k:None for k in parser.keys() }
    return args #, metavars 

from PyQt5.QtCore import QProcess
self = qMainWindow
def runExternalProcess():
    self.message("Executing process.")
    self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
    self.p.start("python3", ['dummy_script.py'])
'''

class DisableEditorDelegate(QtWidgets.QItemDelegate):
    '''QItemDelegate, QAbstractItemDelegate, QStyledItemDelegate
    '''
    def __init__(self, *args, **kwargs):
        super(DisableEditorDelegate, self).__init__(*args, **kwargs)
    def createEditor(self, *args, **kwargs):
        return None 

def slot_currentItemChanged(itemAfter,itemBefore):
    if itemBefore is None:
        print(itemAfter.text(0), itemAfter.text(2),sep='\t')
        return
    print('\tcurrentItemChanged',end='\t')
    print(itemAfter.text(0), itemAfter.text(2),sep='\t')
    print(itemBefore.text(0),itemBefore.text(2),sep='\t')

def slot_itemActivated(*args, **kwargs):
    ''' user open/closed a folded group
    print('slot_itemActivated','args',args,'kwargs',kwargs,sep='\t')
    item, column = args
    '''
    print('\titemActivated',end='\t')

def slot_itemChanged(item, column):
    '''
        print('\nitemChanged','args',args,'kwargs',kwargs,sep='\t')
        print(item.text(0),column, item.text(2))
    '''
    print('\titemChanged col',column,end='\t')
    global args, groups, parser, text
    #TODO if column in [1,3,4]!= 2:
    #    return
    # value is string
    key, value = item.text(0), item.text(2)
    if key in groups:
        #print('ich group',key,value,column)
        return
    #antes=args[key]
    ok = False
    if parser[key]['type'] is str:
        args[key], ok = safe_cast_ok( value, str,   parser[key]['default'])
    elif parser[key]['type'] is int:
        args[key], ok = safe_cast_ok( value, int,   parser[key]['default'])
    elif parser[key]['type'] is float:
        args[key], ok = safe_cast_ok( value, float, parser[key]['default'])
    elif parser[key]['type'] is None:
        if value == 'True':
            args[key] = True
            ok = True
        elif value == 'False':
            args[key] = False
            ok = True
        else:
            ok = False
    else:
        print('Item type %s not implemented!'%parser[key]['type'])
        raise NotImplementedError
    if not ok:
        item.setText( 2, str(parser[key]['default']))
    #print('antes',antes,'despues',args[key],sep='\t')
    #print('end itemChanged',key,value,column)
    cmd = gen_cmd()
    if clipboard_checkBox.isChecked():
        pyperclip.copy(cmd)

def slot_itemClicked(item, column):
    '''CheckState
        Checked             2 The item is checked.
        PartiallyChecked    1 The item is partially checked. Items in hierarchical
                              models may be partially checked if some, but not all,
                              of their children are checked.
        Unchecked           0 The item is unchecked.

        def slot_itemClicked(*args, **kwargs):
            print('\nitemClicked','args',args,'kwargs',kwargs,sep='\t')
            item, column = args
    '''
    print('\titemClicked',end='\t')
    global args, groups, parser, tree, text
    if column != 0:
        return
    # value is string
    key, value = item.text(0), item.text(2)
    #print(key, value, column, item.checkState(0))
    if key in groups:
        parent = item
        group = key
        value = item.checkState(0)
        #print('parent:',parent,'group:',group,'value:',value)
        iterator = QtWidgets.QTreeWidgetItemIterator(tree)
        item: QtWidgets.QTreeWidgetItem = iterator.value()
        while item is not None:
            key = item.text(0)
            if key in groups:
                pass
            elif parser[key]['group'] == group and parser[key]['type'] is None:
                if value == 2:
                    item.setText(2, 'True')
                    args[key] = True
                elif value == 0:
                    item.setText(2, 'False')
                    args[key] = False
                else:
                    pass
                    #print('itemClicked do nothin',key,value)
            else:
                pass
            iterator += 1
            item = iterator.value()
    else:
        antes=args[key]
        if parser[key]['type'] is None:
            if item.checkState(0) == 2:
                args[key] = True
                item.setText(2,'True')
            if item.checkState(0) == 0:
                args[key] = False
                item.setText(2,'False')
        #print('antes',antes,'despues',args[key],sep='\t')
    cmd = gen_cmd()
    if clipboard_checkBox.isChecked():
        pyperclip.copy(cmd)

def slot_itemSelectionChanged(*args, **kwargs):
    print('\nitemSelectionChanged','args',args,'kwargs',kwargs,sep='\t')
    #print('\nitemSelectionChanged',end='\t')

def reloadTree(check_list):
    global args, groups, parser, tree
    iterator = QtWidgets.QTreeWidgetItemIterator(tree)
    item: QtWidgets.QTreeWidgetItem = iterator.value()
    while item is not None:
        key = item.text(0)
        if key not in groups:
            item.setText( 2, str(args[key]))
        item.setCheckState( 0, check_list[key])
        item.setHidden( False)
        iterator += 1
        item = iterator.value()


def slot_buttonGroupClicked(button_id : int):
    '''
        def slot_buttonGroupClicked(*args, **kwargs):
            print('buttonGroupClicked:','args',args,'kwargs',kwargs,sep='\t')
    '''
    global args, groups, parser
    print('buttonGroupClicked:',button_id)
    if button_id == 3:
        dumpState((parser, groups, args, get_check_list()))
    elif button_id == 4:
        parser, groups, args, check_list = loadState()
        reloadTree(check_list)
    else:
        raise NotImplementedError

def init_ButtonGroup(button_group):
    '''        button1.setFont(QtGui.QFont("Sanserif", 15))
        button1.setIcon(QtGui.QIcon("pythonicon.png"))
    '''
    button_sav = QtWidgets.QPushButton('Save')
    button_loa = QtWidgets.QPushButton('Load')
    #button_abo = QtWidgets.QPushButton('Abort')
    #button_run = QtWidgets.QPushButton('Run') 
    #button_group.addButton(button_run, id=1)
    #button_group.addButton(button_abo, id=2)
    button_group.addButton(button_sav, id=3)
    button_group.addButton(button_loa, id=4)
    h_layout = QtWidgets.QHBoxLayout()
    h_layout.addWidget(button_loa)
    h_layout.addWidget(button_sav)
    #h_layout.addWidget(button_abo)
    #h_layout.addWidget(button_run)
    return button_group,h_layout

def gen_cmd():
    global args, parser, tree, text, clipboard_checkBox
    #print('\tgen_cmd',end='\t')
    cmd='python main.py '
    iterator = QtWidgets.QTreeWidgetItemIterator(tree)
    item: QtWidgets.QTreeWidgetItem = iterator.value()
    while item is not None:
        key = item.text(0)
        if key in groups or item.checkState(0)==0:
            pass
        elif parser[key]['type'] is None:
            cmd += parser[key]['option_strings'][0] + ' '
        else:
            cmd += parser[key]['option_strings'][0] + ' ' + str(args[key]) + ' '
        iterator += 1
        item = iterator.value()
    text.setPlainText(cmd)
    return cmd

def get_check_list():
    global tree
    check_list = {}
    iterator = QtWidgets.QTreeWidgetItemIterator(tree)
    item: QtWidgets.QTreeWidgetItem = iterator.value()
    while item is not None:
        check_list[ item.text(0)] = item.checkState(0)
        iterator += 1
        item = iterator.value()
    return check_list

def dumpState( atuple=None):
    '''
        dumpState((parser, groups, args, get_check_list()))
    '''
    pickle.dump( atuple , open('dump.pickle','wb'))

def loadState():
    '''
        parser, groups, args = loadState()
    '''
    return pickle.load( open('dump.pickle','rb'))


def main():
    global args, groups, parser, tree, text, clipboard_checkBox
    #
    args, parser, groups = get_params()
    #
    app      = QtWidgets.QApplication(sys.argv)
    widget   = QtWidgets.QWidget()
    v_layout = QtWidgets.QVBoxLayout()
    # build ui 
    # text browser
    text = QtWidgets.QTextBrowser()
    fm = text.fontMetrics()
    text.setMinimumHeight(fm.height())
    text.setMaximumHeight(4*fm.height())
    text.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents)
    text.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
    v_layout.addWidget(text)
    '''
        text.setPlainText("hello world\n bye !\n bye !\n bye !\n bye !")
        text.setPlaceholderText("hello world\n bye !\n bye !\n bye !\n bye !")
        text.setPlainText("hello world\n bye !\n bye !\n bye !\n bye !")
        QFontMetrics fm(text->font());
        QString myText = text->toPlainText();
        int calcWidth = fm.width(myText);
        int calcHeight = fm.height(myText);
    '''
    # tree
    tree = QtWidgets.QTreeWidget()
    tree = init_Tree(tree)
    v_layout.addWidget(tree)
    # CheckBox browser
    clipboard_checkBox = QtWidgets.QCheckBox('put generated command on system clipboard')
    v_layout.addWidget( clipboard_checkBox)
    # buttons
    button_group = QtWidgets.QButtonGroup()
    button_group, button_group_layout = init_ButtonGroup(button_group )
    v_layout.addLayout( button_group_layout)
    # connnections
    # tree
    #tree.currentItemChanged.connect(slot_currentItemChanged)
    #tree.itemActivated.connect(slot_itemActivated)
    tree.itemChanged.connect(slot_itemChanged)
    tree.itemClicked.connect(slot_itemClicked)
    #tree.itemDoubleClicked.connect(slot_itemDoubleClicked)
    #tree.itemSelectionChanged.connect(slot_itemSelectionChanged)
    # 
    button_group.buttonClicked[int].connect(slot_buttonGroupClicked)
    # 
    # mild consistency check
    if any( g in args.keys() for g in groups):
        offenders = [ g for g in groups if g in args.keys() ]
        text.setPlainText('ERROR: Group name (parser_group.title) in args.dest names:\n\t'\
                            + str(offenders)\
                            +'\nCorrect in ParseInputs.py file')
    gen_cmd()
    widget.setLayout(v_layout)
    # who shows
    show = 'window'
    if show == 'widget':
        widget.show()
    elif show == 'window':
        window = QtWidgets.QMainWindow()
        window.setCentralWidget(widget)
        window.setWindowTitle("Auto Argparse App")
        window.show()
    else:
        print('show what?')
        raise SyntaxError 
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
