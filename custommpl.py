from PyQt4.uic import loadUiType

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)


        self.XView.setChecked(True)
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.X = np.array([])
               
        self.Open.triggered.connect(self.file_open)
        
        self.XView.toggled.connect(lambda: self.btnstate(self.XView))
        self.YView.toggled.connect(lambda: self.btnstate(self.YView))
        self.ZView.toggled.connect(lambda: self.btnstate(self.ZView))
        self.Scroll.sliderMoved.connect(self.sliderval)

    def sliderval(self):
        try:
            if self.XView.isChecked():
                self.im.set_data(self.X[self.Scroll.value(), :, :])
            elif self.YView.isChecked():
                self.im.set_data(self.X[:, self.Scroll.value(), :])
            elif self.ZView.isChecked():
                self.im.set_data(self.X[:, :, self.Scroll.value()])
        except IndexError:
            pass
        self.fig.colorbar(self.im, cax=self.cbaxes)
        self.im.axes.figure.canvas.draw()

    def addmpl(self):
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow)
        self.mplvl.addWidget(self.toolbar)

    def rmmpl(self):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()


    def file_open(self):
        if self.X.size != 0:
            self.rmmpl()
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        ndim = self.showNdimDialog()
        dt = self.showDtDialog()
        try:
            fd = open(name, 'rb')
        except IOError:
            pass
        try:
            self.X = self.readslice(fd, int(ndim), dt)
            self.init_plot()
        except ValueError:
            self.ErrorDialog("Value of Ndim incorrect for this data cube.")

    def btnstate(self, b):
        if b.text()[0] == "X":
            if b.isChecked() == True:
                self.rmmpl()
                self.im = self.ax1.imshow(
                    self.X[self.ind, :, :], cmap='cubehelix', interpolation='nearest')
                self.addmpl()
                self.fig.colorbar(self.im, cax=self.cbaxes)

        if b.text()[0] == "Y":
            if b.isChecked() == True:
                self.rmmpl()
                self.im = self.ax1.imshow(
                    self.X[:, self.ind, :], cmap='cubehelix', interpolation='nearest')
                self.addmpl()
                self.fig.colorbar(self.im, cax=self.cbaxes)
                
        if b.text()[0] == "Z":
            if b.isChecked() == True:
                self.rmmpl()
                self.im = self.ax1.imshow(
                    self.X[:, :, self.ind], cmap='cubehelix', interpolation='nearest')
                self.addmpl()
                self.fig.colorbar(self.im, cax=self.cbaxes)
        
    def init_plot(self, ):
        self.addmpl()
        self.cbaxes = fig.add_axes([0.85, 0.1, 0.03, 0.8])
        rows, cols, self.slices = self.X.shape
        self.ind = self.slices / 2
        self.im = self.ax1.imshow(self.X[self.ind, :, :],
                            cmap='cubehelix', interpolation='nearest')
        self.fig.colorbar(self.im, cax=self.cbaxes)
        self.Scroll.setMaximum(self.slices)
        self.Scroll.setValue(self.ind)

    def readslice(self, fd, ndim, dt):
        if dt == np.float64:
            dim = 16
        elif dt == np.float32:
            dim = 4
        shape = (ndim, ndim, ndim, dim)
        data = np.fromfile(
            file=fd, dtype=dt, sep="").reshape(shape, order='F')
        fd.close()
        data = data[:, :, :, 0]
        data = data[:, :, :]
        return data

    def showNdimDialog(self, ):
        text, ok = QtGui.QInputDialog.getInt(self, 'Input Ndim', 'Enter Ndim:')
        if ok:
            return text
            
    def showDtDialog(self, ):
        items = ("Real*4", "Real*8")
		
        item, ok = QtGui.QInputDialog.getItem(self, "Select Fortran Precision", 
         "List of Precisions", items, 0, False)
			
        if ok and item:
            if item == "Real*8":
                item = np.float64
            elif item == "Real*4":
                item = np.float32
            return item

    def ErrorDialog(self, ErrMsg):
        QtGui.QMessageBox.warning(self, "Error", ErrMsg)

if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np
    import matplotlib.pyplot as plt
    fig = Figure()
    ax = fig.add_subplot(111)

    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
