#NOREPLENV: /home/fdo/source/C2FSBd/venv
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys

import pickle
from argparse import Namespace
from ParseInputs import Parser

app    = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
tree   = QtWidgets.QTreeWidget()

def get_args(parser):
    parser = { a.dest : a.__dict__ for a in Parser()._get_optional_actions() }
    parser.pop('help')
    #metavars = set( v['metavar'] for k,v in parser.items())
    args = { k:None for k in parser.keys() }
    return args #, metavars 

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
parser = Parser()
parser, groups = get_grouped_parser(parser)
args = { g:None for g in groups }

def slot_currentItemChanged(itemAfter,itemBefore):
    if itemBefore is None:
        print(itemAfter.text(0), itemAfter.text(2),sep='\t')
        return
    print(itemAfter.text(0), itemAfter.text(2),sep='\t')
    print(itemBefore.text(0),itemBefore.text(2),sep='\t')

def slot_itemActivated(*args, **kwargs):
    ''' user open/closed a folded group
        item, column = args
    '''
    print('\nslot_itemActivated','args',args,'kwargs',kwargs,sep='\t')

def slot_itemChanged(item, column):
    '''
        print('\nitemChanged','args',args,'kwargs',kwargs,sep='\t')
        print(item.text(0),column, item.text(2))
    '''
    global args
    if column != 2:
        return
    # value is string
    key, value = item.text(0), item.text(2)
    if key not in args.keys():
        return
    antes=args[key]
    if parser[key]['type'] is str:
        args[key] = value
    elif parser[key]['type'] is int:
        args[key] = int(value)
    elif parser[key]['type'] is float:
        args[key] = float(value)
    elif parser[key]['type'] is None and value == 'True':
        args[key] = True
    elif parser[key]['type'] is None and value == 'False':
        args[key] = False
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
            print('\nitemClicked','args',args,'kwargs',kwargs,sep='\t')
            item, column = args
    '''
    global args
    if column != 0:
        return
    # value is string
    key, value = item.text(0), item.text(2)
    #print(key, value, column, item.checkState(0))
    if key in groups:
        parent = item
        group = key
        value = item.checkState(0)
        print('parent:',parent,'group:',group,'value:',value)
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
                    print('do nothin')
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
        print('antes',antes,'despues',args[key],sep='\t')

def slot_itemSelectionChanged(*args, **kwargs):
    '''
    '''
    print('\nitemSelectionChanged','args',args,'kwargs',kwargs,sep='\t')

def main():
    global app
    global window
    global tree
    global args

    window.setWindowTitle("Auto python argparse app")
    tree.setHeaderLabels(['dest','option_strings[0]','default->args.dest=value','type','help'])

    #for group in groups:
    #    for key,val in args.items():
    #        if val['group'] == group:
    #            print(group,key,val['group'] )

    tree.setColumnCount(5)
    for group in groups:
        parent = QtWidgets.QTreeWidgetItem(tree)
        parent.setText(0, group)
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        #if group is None:
        #    parent.setExpanded(False)
        #else:
        #    parent.setExpanded(True)
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
                    if val['default'] == True:
                        child.setCheckState(0, Qt.Checked)
                        args[key] = True
                    if val['default'] == False:
                        child.setCheckState(0, Qt.Unchecked)
                        args[key] = False
                child.setText(2, str(val['default']))
                args[key] = str(val['default'])
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
