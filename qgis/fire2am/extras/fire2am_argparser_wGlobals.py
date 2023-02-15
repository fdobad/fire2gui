#!/usr/bin/env python3
#NOREPLENV: /home/fdo/pyvenv/qgis
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys, pickle
from argparse import Namespace
from ParseInputs import Parser
import pyperclip
def safe_cast_ok(val, to_type, default=None):
    try:
        return to_type(val), True
    except (ValueError, TypeError):
        return default, False

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

def init_Tree(tree):
    global args, groups, parser
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

def get_params():
    global args, groups, parser
    parser, groups = get_grouped_parser(Parser())
    args = { dest:parser[dest]['default'] for dest in parser.keys() }
    return args, parser, groups

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
