from PyQt4.uic import loadUiType

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import gc

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
        self.im.autoscale()
        
    def file_open(self):
        try:
            self.fig.delaxes(self.fig.axes[1])
            self.figure.subplots_adjust(right=0.90)
        except IndexError:
            pass
        except AttributeError:
            pass
        if self.X.size != 0:
            self.rmmpl()
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        ndim = self.showNdimDialog()
        item = str(self.showDtDialog())

        if "Real*8" in item:
            dt = np.float64
        elif "Real*4" in item:
            dt = np.float32
        
        if "4 dim" in item:
            dim = 4
        elif "3 dim" in item:
            dim = 3
        
        try:
            fd = open(name, 'rb')
        except IOError:
            pass
        try:
            self.X = self.readslice(fd, int(ndim), dt, dim)
            self.init_plot()
        except ValueError:
            self.ErrorDialog("Value of Ndim incorrect for this data cube.")
            self.rmmpl()
    
    def btnstate(self, b):
        if b.text()[0] == "X":
            if b.isChecked() is True:
                self.rmmpl()
                self.im = self.ax1.imshow(self.X[self.ind, :, :],
                                          cmap='cubehelix', interpolation='nearest')
                self.addmpl()

        if b.text()[0] == "Y":
            if b.isChecked() is True:
                self.rmmpl()
                self.im = self.ax1.imshow(
                    self.X[:, self.ind, :], cmap='cubehelix', interpolation='nearest')
                self.addmpl()

        if b.text()[0] == "Z":
            if b.isChecked() is True:
                self.rmmpl()
                self.im = self.ax1.imshow(
                    self.X[:, :, self.ind], cmap='cubehelix', interpolation='nearest')
                self.addmpl()

    def init_plot(self, ):
        self.XView.setChecked(True)
        self.addmpl()
        rows, cols, self.slices = self.X.shape
        self.ind = self.slices / 2
        self.im = self.ax1.imshow(self.X[self.ind, :, :],
                                  cmap='cubehelix', interpolation='nearest')
        self.fig.colorbar(self.im)
        self.Scroll.setMaximum(self.slices)
        self.Scroll.setValue(self.ind)

    def readslice(self, fd, ndim, dt, dim):
        if dim == 4:
            if dt == np.float64:
                magic = 16
            elif dt == np.float32:
                magic = 4
            shape = (ndim, ndim, ndim, magic)
        elif dim == 3:
            shape = (ndim, ndim, ndim)
        data = np.fromfile(
            file=fd, dtype=dt, sep="").reshape(shape, order='F')
        fd.close()
        if dim == 4:
            data = data[:, :, :, 0]
        data = data[:, :, :]
        gc.collect()
        return data

    def showNdimDialog(self, ):
        text, ok = QtGui.QInputDialog.getInt(self, 'Input Ndim', 'Enter Ndim:')
        if ok:
            return text

    def showDtDialog(self, ):
        items = ("4 dim Real*4", "4 dim Real*8", "3 dim Real*4", "3 dim Real*8")

        item, ok = QtGui.QInputDialog.getItem(self, "Select Fortran Precision",
                                              "Precisions", items, 0, False)

        if ok and item:                     
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
    
    gc.enable()
    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
