#NOREPLENV: /home/fdo/source/C2FSBd/venv
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys

import pickle
from argparse import Namespace
from ParseInputs import Parser
#import pyperclip

app     = QtWidgets.QApplication(sys.argv)

window = QtWidgets.QMainWindow()
window.setLayout(QtWidgets.QGridLayout())

tree    = QtWidgets.QTreeWidget()
#tree.setLayout(QtWidgets.QGridLayout())

def get_parser_added_arguments_2dict(parser):
    # no groups
    parser = { a.dest : a.__dict__ for a in Parser()._get_optional_actions() }
    parser.pop('help')
    #metavars = set( v['metavar'] for k,v in parser.items()) chanta!
    args = { k:None for k in parser.keys() }
    return args

parser = Parser()
def get_parser_grouped_added_arguments_2dict(parser):
    '''see usr/lib/python39/argparse.py for details
        groups are stored on _action_groups, lines: 1352, 1448

        groups = set( v['metavar'] for k,v in parser.items())
        args = { k:None for k in parser.keys() }
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

    s = {}
    for k,v in q.items():
        s[k] =  { a.dest : a.__dict__ for a in v }
        s[k]['group'] = k

    return s


def slot_currentItemChanged(itemAfter,itemBefore):
    if itemBefore is None:
        print(itemAfter.text(0), itemAfter.text(2),sep='\t')
        return
    print(itemAfter.text(0), itemAfter.text(2),sep='\t')
    print(itemBefore.text(0),itemBefore.text(2),sep='\t')

def slot_itemActivated(*args, **kwargs):
    print('\nslot_itemActivated','args',args,'kwargs',kwargs,sep='\t')

def slot_itemChanged(item, column):
    '''
        print('\nitemChanged','args',args,'kwargs',kwargs,sep='\t')
        print(item.text(0),column, item.text(2))
    '''
    global args
    # value is string
    key, value = item.text(0), item.text(2)
    if column != 2 or key not in args.keys():
        return
    antes=args[key]
    if parser['type'] is str:
        args[k] = value
    elif parser['type'] is int:
        args[k] = int(value)
    elif parser['type'] is float:
        args[k] = float(value)
    elif parser['type'] is None and value == 'True':
        args[k] = True
    elif parser['type'] is None and value == 'False':
        args[k] = False
    else:
        raise NotImplementedError
    print('antes',antes,'despues',args[key],sep='\t')

def q2b(q):
    if q==0:
        return False
    elif q==2:
        return True
    else:
        raise TypeError

def slot_itemClicked(item, column):
    '''CheckState
        Checked             2 The item is checked.
        PartiallyChecked    1 The item is partially checked. Items in hierarchical
                              models may be partially checked if some, but not all,
                              of their children are checked.
        Unchecked           0 The item is unchecked.

        def slot_itemClicked(*args, **kwargs):
            global args
            print('\nitemClicked','args',args,'kwargs',kwargs,sep='\t')
            item, column = args
    '''
    global args
    # value is string
    key, value = item.text(0), item.text(2)
    #print(key, value, column, item.checkState(0))
    if column != 0:
        return
    if key in metavars:
        # TODO activar hartos
        return
    antes=args[key]
    if parser[key]['type'] is None:
        if item.checkState(0)==2: # checked
            args[key] = True
            item.setText(2,'True')
        if item.checkState(0)==0: # checked
            args[key] = False
            item.setText(2,'False')
    print('antes',antes,'despues',args[key],sep='\t')

def slot_itemSelectionChanged(*args, **kwargs):
    print('\nitemSelectionChanged','args',args,'kwargs',kwargs,sep='\t')

def main():
    global app
    global window
    global tree
    global args

    window.setWindowTitle("Auto python argparse app")
    tree.setHeaderLabels(['dest','option_strings[0]','default->args.dest=value','type','help'])

    tree.setColumnCount(5)
    for meta in metavars:
        parent = QtWidgets.QTreeWidgetItem(tree)
        parent.setText(0, "{}".format(meta))
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        if meta is None:
            parent.setExpanded(False)
        else:
            parent.setExpanded(True)
        for key,val in parser.items():
            if val['metavar']== meta:
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
                child.setText(0, "{}".format(val['dest']))
                child.setText(1,val['option_strings'][0])
                #if val['type'] is None:
                #    child.setText(3,'bool (None)'))
                #else:
                #    child.setText(3,str(val['type']))
                child.setText(3,str(val['type']))
                child.setText(4,val['help'])
                child.setCheckState(0, Qt.Unchecked)
                if isinstance(val['default'], bool):
                    if val['default'] == True:
                        child.setCheckState(0, Qt.Checked)
                        args[key]=True
                    if val['default'] == False:
                        child.setCheckState(0, Qt.Unchecked)
                        args[key]=False
                child.setText(2,str(val['default']))
                args[key]=val['default']
                child.setHidden(False)

    tree.currentItemChanged.connect(slot_currentItemChanged)
    tree.itemActivated.connect(slot_itemActivated)
    tree.itemChanged.connect(slot_itemChanged)
    tree.itemClicked.connect(slot_itemClicked)
    tree.itemSelectionChanged.connect(slot_itemSelectionChanged)
    tree.AdjustToContentsOnFirstShow
    tree.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    '''
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
    '''

    '''
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
    '''
