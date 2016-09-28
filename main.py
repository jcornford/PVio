import sys
import os
import numpy as np
import pandas as pd
from PyQt4 import QtGui#,# uic
from PyQt4.QtCore import QThread, SIGNAL
import pyqtgraph as pg

import design

class PVio(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PVio, self).__init__(parent)
        self.setupUi(self)
        #self.home = '/home'
        self.data_obj = None
        self.home = '/Users/jonathan/PhD/Data/PV_dendritic_intergration/Data'
        self.home = '/Users/jonathan/PhD/Data/PV_dendritic_intergration/Data/2016_05/2016_05_11/'

        self.btnBrowse.clicked.connect(self.browse_folder)
        self.load_file_btn.clicked.connect(self.load_file)

        self.plot_1 = self.GraphicsLayoutWidget.addPlot()
        self.traceSelector.valueChanged.connect(self.plot_traces)
        self.channel_selector.valueChanged.connect(self.plot_traces)

        #self.treeWidget.setColumnCount(1)
        items = []
        for i in range(10):
            item = QtGui.QTreeWidgetItem([str(i)])
            for string_ in ["erfer","gergfre","erg"]:
                item.addChild(QtGui.QTreeWidgetItem([string_]))
            items.append(item)
        self.treeWidget.addTopLevelItems(items)

        self.treeWidget.itemSelectionChanged.connect(self.tree_selection)


        #self.load_file('/Users/jonathan/PhD/Data/PV_dendritic_intergration/Data/2016_05/2016_05_11/2016_05_11_slice1_cell1_cf2.ASC')
    def tree_selection(self):
        parent = self.treeWidget.currentItem().parent()
        if parent:
            root = parent.text(0)
            print(root)
        item = self.treeWidget.currentItem().text(0)
        print(item)

    def plot_traces(self):
        t_i = self.traceSelector.value()
        channel = self.channel_selector.value()
        if self.data_obj is not None:
            if not self.holdPlot.isChecked():
                self.plot_1.clear()
            self.plot_1.addItem(pg.PlotCurveItem(self.data_obj[channel][:,t_i]))

    def browse_folder(self):
        self.listWidget.clear()
        directory = QtGui.QFileDialog.getExistingDirectory(self, "Pick a folder", self.home)
        if directory:
            for file_name in os.listdir(directory):
                self.listWidget.addItem(file_name)

    def load_file(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
               self.home)
        self.loading_thread = LoadFileThread(fname)
        #self.connect(self.loading_thread, SIGNAL("finished()"), self.done)
        self.connect(self.loading_thread, SIGNAL("catch_data(PyQt_PyObject)"), self.catch_data)
        self.loading_thread.start()

    def catch_data(self, data_obj):
        self.data_obj = data_obj
        #print(data_obj)
        #print(data_obj.channel_0[:,5])
        #print(data_obj.channel_0[:,5].shape)
        self.plot_traces()

    def done(self):
        QtGui.QMessageBox.information(self, "Done!", "Done loading!")


class LoadFileThread(QThread):

    def __init__(self, filename):
        QThread.__init__(self)
        self.filename = filename

    def __del__(self):
        self.wait()

    def load_file(self, filename):
        self.data_obj = LabViewDATFile(filename, channel_number = 4)

    def run(self):
        print('sup, loading: '+self.filename)
        self.load_file(self.filename)
        self.emit(SIGNAL('catch_data(PyQt_PyObject)'), self.data_obj)

class LabViewDATFile():
    def __init__(self, filename, channel_number = 4):
            self.filename  = filename
            self.channel_number = channel_number
            self.channel_dict = {}
            self.load_data()

    def __getitem__(self, item):
        return self.channel_dict[item]

    def load_data(self):
            with open(self.filename) as f:
                ncols = len(f.readline().split('\t'))
            data = pd.read_table(self.filename, index_col=False,  header= None,
                                 dtype=np.float, usecols= range(2, ncols), engine = 'c',
                                 low_memory=False, na_filter=False).values.T
            self.time = data[:,0]
            for i in range(self.channel_number):
                self.channel_dict[i] = data[:, i+1::self.channel_number]

def main():
    app = QtGui.QApplication(sys.argv)
    form = PVio()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()

