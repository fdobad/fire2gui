from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys

def getC2Fargs():
    from C2FSB.Cell2Fire import ParseInputs
    
    parser = ParseInputs.Parser()
    opac = parser._get_optional_actions()
    '''
    pars = { sa.dest : { 'optstr' : sa.option_strings[0], 'type': sa.type, 'default': sa.default, 'help':sa.help} for sa in opac[1:] }
    assert parser.__dict__['_actions'] == parser._get_optional_actions()
    '''
    pars = { a.dest : a.__dict__ for a in parser._get_optional_actions() }


def main():
    app     = QtWidgets.QApplication(sys.argv)
    tree    = QtWidgets.QTreeWidget()
    headerItem  = QtWidgets.QTreeWidgetItem()
    item    = QtWidgets.QTreeWidgetItem()

    tree.setColumnCount(3)
    arr={'InFolder': {'optstr': '--input-instance-folder','type': str,'default': None},
        'OutFolder': {'optstr': '--output-folder', 'type': str, 'default': None},
        'sim_years': {'optstr': '--sim-years', 'type': int, 'default': 1},
        'nsims': {'optstr': '--nsims', 'type': int, 'default': 1},}

    for i in range(3):
        parent = QtWidgets.QTreeWidgetItem(tree)
        parent.setText(0, "Parent {}".format(i))
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for x in range(5):
            child = QtWidgets.QTreeWidgetItem(parent)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, "Child {}".format(x))
            child.setCheckState(0, Qt.Unchecked)
    tree.show() 
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
