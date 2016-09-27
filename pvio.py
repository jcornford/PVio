import sys
from PyQt4 import QtGui

import sys
import os
from PyQt4 import QtGui

class load_labview_ASC:

    '''
    10.10.2014: Heavily used, but most likely in need of improvement.

    This class creates a data object from labview ASC files.  Channels are attributes of the object,
    and are 2d arrays. Rows are datapoints, columns are individual sweeps.

    Channel number is restricted to 2 or 4 channels.

    pass me the full path of the file
    '''
    def __init__(self,filename, channel_number):
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


class PVio(QtGui.QMainWindow):

    def __init__(self):
        super(PVio, self).__init__()

        self.initUI()

    def initUI(self):

        self.home = '/Users/jonathan/PhD/Data/PV_dendritic_intergration/Data'
        if not os.path.exists(self.home):
            self.home = '/home'

        self.textEdit = QtGui.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        open_file = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Load File')
        open_file.triggered.connect(self.showDialog)

        set_home = QtGui.QAction(QtGui.QIcon(), 'Set home folder', self)
        set_home.setStatusTip('Set Home')
        set_home.setShortcut('Ctrl+1')
        set_home.triggered.connect(self.select_home)

        clean_folder = QtGui.QAction(QtGui.QIcon(), 'Clean folder', self)
        clean_folder.setShortcut('Ctrl+2')
        clean_folder.setStatusTip('Clean up directory')
        clean_folder.triggered.connect(self.clean_asc_time_dat)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(open_file)
        fileMenu.addAction(set_home)
        fileMenu.addAction(clean_folder)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('PVio')
        self.show()

    def clean_asc_time_dat(self):
        "inherit this from phd module"
        print('not coded yet')
        pass

    def select_home(self):
        self.home = QtGui.QFileDialog.getExistingDirectory(self, 'Open file', '/home')
        print(self.home)

    def showDialog(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
               self.home )
        self.textEdit.setText(fname)

        #f = open(fname, 'r')

        #with f:
        #    data = f.read()
        #    self.textEdit.setText(data)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = PVio()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()