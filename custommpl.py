from PyQt4.uic import loadUiType
 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, X, fig, ax):
        super(Main, self).__init__()
        self.setupUi(self)
        
        self.Open.triggered.connect(self.file_open)
        self.XView.setChecked(True)
        
        self.XView.toggled.connect(lambda:self.btnstate(self.XView))
        self.YView.toggled.connect(lambda:self.btnstate(self.YView))
        self.ZView.toggled.connect(lambda:self.btnstate(self.ZView))
                
        self.X = X
        rows, cols, self.slices = X.shape
        self.ind = self.slices / 2
        self.im = ax.imshow(self.X[self.ind, :, :], cmap='cubehelix', interpolation='nearest')
        fig.colorbar(self.im)
        self.Scroll.setMaximum(self.slices)
        self.Scroll.setValue(self.ind)
        self.Scroll.sliderMoved.connect(self.sliderval)
        
    
    def sliderval(self):
        self.im.set_data(self.X[self.Scroll.value(), :, :])
        self.im.axes.figure.canvas.draw()
        
    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()

    def file_open(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        fd = open(name , 'rb')
        
        
    def btnstate(self,b):
        if b.text()[0] == "X":
         if b.isChecked() == True:
            print b.text()+" is selected"
         else:
            print b.text()+" is deselected"
	
        if b.text()[0] == "Y":
         if b.isChecked() == True:
            print b.text()+" is selected"
            self.im = ax.imshow(self.X[:, self.ind, :], cmap='cubehelix', interpolation='nearest')
         else:
            print b.text()+" is deselected"
            
        if b.text()[0] == "Z":
         if b.isChecked() == True:
            print b.text()+" is selected"
            self.im = ax.imshow(self.X[:, :, self.ind], cmap='cubehelix', interpolation='nearest')
         else:
            print b.text()+" is deselected"

def readslice(inputfilename, ndim):
    shape = (ndim, ndim, ndim, 4)
    fd = open('tmp.dat', 'rb')
    data = np.fromfile(
        file=fd, dtype=np.float32,sep="").reshape(shape, order='F')
    fd.close()
    data = data[:, :, :, 0]
    return data
        
if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np
    import matplotlib.pyplot as plt
 
    fig = Figure()
    ax = fig.add_subplot(111)
    Z = np.loadtxt('blue.dat')
    X = readslice('tmp.dat', int(201))
    X= X[:,:,:]
#    im = ax.imshow(X, cmap='hot')
#    fig1.colorbar(im, orientation='vertical')
 
    app = QtGui.QApplication(sys.argv)
    main = Main(X, fig, ax)
    main.addmpl(fig)
    main.show()
    sys.exit(app.exec_())
