import sys
import os
import numpy as np
from PyQt4 import QtGui#,# uic
from PyQt4.QtCore import QThread, SIGNAL
import pyqtgraph as pg

import design

class PVio(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PVio, self).__init__(parent)
        self.setupUi(self)
        #uic.loadUi('design.ui', self)
        #self.home = '/home'
        self.home = '/Users/jonathan/PhD/Data/PV_dendritic_intergration/Data'

        self.btnBrowse.clicked.connect(self.browse_folder)
        self.load_file_btn.clicked.connect(self.load_file)

        self.plot_1 = self.GraphicsLayoutWidget.addPlot()


    def browse_folder(self):
        self.listWidget.clear()
        directory = QtGui.QFileDialog.getExistingDirectory(self, "Pick a folder",
                                                           self.home)

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
        print(data_obj)
        #self.listWidget.addItem(str(data_obj))
        print(data_obj.channel_0[:,5])
        print(data_obj.channel_0[:,5].shape)
        self.plot_1.addItem(pg.PlotCurveItem(data_obj.channel_0[1:, 5]))
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
    def __init__(self, filename, channel_number):
            #start = time.time()
            self.filename  = filename
            self.channel_number = channel_number
            try:
                self.data = np.loadtxt(self.filename,dtype = 'float', skiprows = 1)
                self.data = np.transpose(self.data)
                self.data = self.data[:-1,:] # we need to remove the last value of the data as there is one less timescale value, this is a hack though
                self.time = np.loadtxt(self.filename,dtype = str, skiprows = 0)
            except Exception:
                print('Error loading file')

            try:
                self.time = self.time[0,1:] # slice to remove 'time' string and other datapoints.
                self.timescale = self.time.astype('float')
                #self.timescale = [float(s) for s in self.time]

                #print(self.timescale[-1], 'ms is the last timepoint.')
                #print('There are',len(self.timescale), 'time-points in this timescale.')
            except Exception:
                print('Something went wrong with the timescale conversion')

            #print(self.data.shape, 'is the data shape') # axis 0 = down, 1 = across, 2 = 3d.
            self.trial_number = (self.data.shape[1]/self.channel_number)
            #print('A', self.trial_number, 'sweep data-set has been loaded.')
            if self.channel_number == 4:
                self.channel_0 = self.data[:,0::4]
                self.channel_1 = self.data[:,1::4]
                self.channel_2 = self.data[:,2::4]
                self.channel_3 = self.data[:,3::4]
                self.data_matrix = np.dstack((self.channel_0,self.channel_1,self.channel_2,self.channel_3))

            elif self.channel_number == 2:
                self.channel_0 = self.data[:,0::2]
                self.channel_1 = self.data[:,1::2]
                self.data_matrix = np.dstack((self.channel_0,self.channel_1))

            else:
                print('Unsupported number of channels entered')

def main():
    app = QtGui.QApplication(sys.argv)
    form = PVio()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()

