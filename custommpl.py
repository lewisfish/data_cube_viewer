from PyQt4.uic import loadUiType

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui')


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self, fig, ax):
        super(Main, self).__init__()
        self.setupUi(self)

        self.Open.triggered.connect(self.file_open)
        self.XView.setChecked(True)
        self.fig = fig
        self.XView.toggled.connect(lambda: self.btnstate(self.XView))
        self.YView.toggled.connect(lambda: self.btnstate(self.YView))
        self.ZView.toggled.connect(lambda: self.btnstate(self.ZView))

        self.X = []

        self.Scroll.sliderMoved.connect(self.sliderval)

    def sliderval(self):
        if self.XView.isChecked():
            self.im.set_data(self.X[self.Scroll.value(), :, :])
        elif self.YView.isChecked():
            self.im.set_data(self.X[:, self.Scroll.value(), :])
        elif self.ZView.isChecked():
            self.im.set_data(self.X[:, :, self.Scroll.value()])
        self.im.axes.figure.canvas.draw()

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()

    def rmmpl(self):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()

    def file_open(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        ndim = self.showNdimDialog()
        try:
            fd = open(name, 'rb')
        except IOError:
            pass
        try:
            self.X = self.readslice(fd, int(ndim))
            self.init_plot()
        except ValueError:
            self.ErrorDialog("Value of Ndim incorrect for this data cube.")

    def btnstate(self, b):
        if b.text()[0] == "X":
            if b.isChecked() == True:
                self.rmmpl()
                self.im = ax.imshow(
                    self.X[self.ind, :, :], cmap='cubehelix', interpolation='nearest')
                self.addmpl(self.fig)

        if b.text()[0] == "Y":
            if b.isChecked() == True:
                self.rmmpl()
                self.im = ax.imshow(
                    self.X[:, self.ind, :], cmap='cubehelix', interpolation='nearest')
                self.addmpl(self.fig)

        if b.text()[0] == "Z":
            if b.isChecked() == True:
                self.rmmpl()
                self.im = ax.imshow(
                    self.X[:, :, self.ind], cmap='cubehelix', interpolation='nearest')
                self.addmpl(self.fig)

    def init_plot(self, ):
        self.addmpl(self.fig)
        rows, cols, self.slices = self.X.shape
        self.ind = self.slices / 2
        self.im = ax.imshow(self.X[self.ind, :, :],
                            cmap='cubehelix', interpolation='nearest')
        self.fig.colorbar(self.im)
        self.Scroll.setMaximum(self.slices)
        self.Scroll.setValue(self.ind)

    def readslice(self, fd, ndim):
        shape = (ndim, ndim, ndim, 4)
        data = np.fromfile(
            file=fd, dtype=np.float32, sep="").reshape(shape, order='F')
        fd.close()
        data = data[:, :, :, 0]
        data = data[:, :, :]
        return data

    def showNdimDialog(self, ):
        text, ok = QtGui.QInputDialog.getInt(self, 'Input Ndim', 'Enter Ndim:')
        if ok:
            return text

    def ErrorDialog(self, ErrMsg):
        QtGui.QMessageBox.warning(self, "Error", ErrMsg)

if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np
    import matplotlib.pyplot as plt

    fig = Figure()
    ax = fig.add_subplot(111)
#    Z = np.loadtxt('blue.dat')
##    X = readslice('tmp.dat', int(201))
##    X= X[:,:,:]
##    im = ax.imshow(X, cmap='hot')
##    fig1.colorbar(im, orientation='vertical')

    app = QtGui.QApplication(sys.argv)
    main = Main(fig, ax)
#    main.addmpl(fig)
    main.show()
    sys.exit(app.exec_())
