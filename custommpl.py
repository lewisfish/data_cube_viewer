#!/usr/bin/python
from PyQt4.uic import loadUiType

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('/home/lewis/data_cube/mainwindow.ui')


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.flag = 0
        self.ave = np.array([])

        self.XView.setChecked(True)
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.X = np.array([])

        self.XView.toggled.connect(lambda: self.btnstate(self.XView))
        self.YView.toggled.connect(lambda: self.btnstate(self.YView))
        self.ZView.toggled.connect(lambda: self.btnstate(self.ZView))
        self.Bore.toggled.connect(lambda: self.btnstate(self.Bore))
        self.AverageBore.toggled.connect(
            lambda: self.btnstate(self.AverageBore))

        self.Scroll_Horz.sliderMoved.connect(self.sliderval)
        self.Scroll_Vert.sliderMoved.connect(self.sliderval)

        if len(sys.argv) >= 2:
            self.file_open(sys.argv[1:4])
        self.Open.triggered.connect(self.file_open)
        self.Reset.triggered.connect(self.reset_plot)

    def sliderval(self):
        try:
            if self.XView.isChecked():
                self.im.set_data(self.X[self.Scroll_Vert.value(), :, :])
            elif self.YView.isChecked():
                self.im.set_data(self.X[:, self.Scroll_Vert.value(), :])
            elif self.ZView.isChecked():
                self.im.set_data(self.X[:, :, self.Scroll_Vert.value()])
            elif self.Bore.isChecked():
                self.im.set_ydata(
                    self.X[self.Scroll_Horz.value(), self.Scroll_Vert.value(), :][::-1])
            elif self.AverageBore.isChecked():
                self.Scroll_Horz.setValue(self.ind)
                self.Scroll_Vert.setValue(self.ind)
        except IndexError:
            pass
        
        try:
            self.im.axes.figure.canvas.draw()
            # self.im.autoscale()
        except AttributeError:
            pass

    def addmpl(self):
        self.flag = 1
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
        # self.im.autoscale()

    def file_open(self, *args):
        if self.flag == 1:
            self.reset_plot()
        try:
            self.reset_plot()
        except:
            pass
        if args[0]:
            args = args[0]
            name = args[0]
            if len(args) == 2:
                ndim = args[1]
                item = str(self.showDtDialog())

            elif len(args) == 3:
                ndim = args[1]
                item = args[2]

                if int(item) == 1:
                    item = str("4 dim Real*4")
                elif int(item) == 2:
                    item = str("4 dim Real*8")
                elif int(item) == 3:
                    item = "3 dim Real*4"
                elif int(item) == 4:
                    item = "3 dim Real*8"
            else:
                ndim = self.showNdimDialog()
                item = str(self.showDtDialog())
            args = None
        else:
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
            #del self.X
            self.readslice(fd, int(ndim), dt, dim)
            self.init_plot()
        except ValueError:
            self.ErrorDialog("Value of Ndim incorrect for this data cube.")
            # self.rmmpl()

    def btnstate(self, b):

        if b.text() == "X View":
            if b.isChecked() is True:
                self.reset_plot()
                self.im = self.ax1.matshow(self.X[self.ind, :, :],
                                           cmap='cubehelix', interpolation='nearest')
                self.fig.colorbar(self.im) 
                self.addmpl()

        if b.text() == "Y View":
            if b.isChecked() is True:
                self.reset_plot()
                self.im = self.ax1.matshow(
                    self.X[:, self.ind, :], cmap='cubehelix', interpolation='nearest')
                self.fig.colorbar(self.im)
                self.addmpl()

        if b.text() == "Z View":
            if b.isChecked() is True:
                self.reset_plot()
                self.im = self.ax1.matshow(
                    self.X[:, :, self.ind], cmap='cubehelix', interpolation='nearest')
                self.fig.colorbar(self.im)
                self.addmpl()

        if b.text() == "Draw Bore":
            if b.isChecked() is True:
                self.reset_plot()
                self.im, = self.ax1.plot(self.X[self.ind, self.ind, :][::-1])
                self.addmpl()

        if b.text() == "Avg. Bore":
            if b.isChecked() is True:
                self.reset_plot()

                if len(self.ave) == 0:
                    self.ave = np.array([])
                    self.ave = np.sum(self.X, (0, 1))
                    self.ave /= (len(self.X[0]) * len(self.X[1]))

                self.im = self.ax1.plot(self.ave[::-1])
                self.addmpl()

    def reset_plot(self, ):
        self.ave = np.array([])
        self.fig.clf()
        self.ax1.clear()
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        try:
            self.fig.delaxes(self.fig.axes[1])
            self.figure.subplot_adjust(right=0.90)
        except IndexError:
            pass
        except AttributeError:
            pass
        self.rmmpl()

    def init_plot(self, ):
        self.XView.setChecked(True)
        self.addmpl()
        rows, cols, self.slices = self.X.shape
        self.ind = self.slices / 2
        self.im = self.ax1.matshow(self.X[self.ind, :, :],
                                   cmap='cubehelix', interpolation='nearest')
        self.fig.colorbar(self.im)
        self.Scroll_Horz.setMaximum(self.slices)
        self.Scroll_Horz.setValue(self.ind)
        self.Scroll_Vert.setMaximum(self.slices)
        self.Scroll_Vert.setValue(self.ind)

    def readslice(self, fd, ndim, dt, dim):
        if dim == 4:
            if dt == np.float64:
                magic = 4        # !this sometimes needs changed try powers of 2...
            elif dt == np.float32:
                magic = 4
            shape = (ndim, ndim, ndim, magic)
        elif dim == 3:
            shape = (ndim, ndim, ndim)
        data = np.fromfile(
            file=fd, dtype=dt, sep="")
#        print len(data)
        data = data.reshape(shape, order='F')
        fd.close()
        if dim == 4:
            data = data[:, :, :, 0]
        self.X = data[:, :, :]
        del data

    def showNdimDialog(self, ):
        text, ok = QtGui.QInputDialog.getInt(self, 'Input Ndim', 'Enter Ndim:')
        if ok:
            return text

    def showDtDialog(self, ):
        items = ("4 dim Real*4", "4 dim Real*8",
                 "3 dim Real*4", "3 dim Real*8")

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
    
    if len(sys.argv) >=2:
        if 'help' in str(sys.argv[1]) or str(sys.argv[1])=='-h':
            print '\nUsage: d3v [FILE] [NDIM] [FP_REP+DIM](1-4)'

            print'\nNDIM, \t    gives the dimensions of the data cube to be examined'
            print'FP_REP+DIM, gives choice of(1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8'
            print'\t    (1)\t\t  (2)\t\t(3)\t      (4)\n'
            sys.exit(0)
            
        elif len(sys.argv) < 3 and len(sys.argv) > 2:
            print '\nUsage: d3v [FILE] [NDIM] [FP_REP+DIM](1-4)'

            print'\nNDIM, \t    gives the dimensions of the data cube to be examined'
            print'FP_REP+DIM, gives choice of(1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8'
            print'\t    (1)\t\t  (2)\t\t(3)\t      (4)\n'
            sys.exit(0)
    else:
        print '\nUsage: d3v [FILE] [NDIM] [FP_REP+DIM](1-4)'

        print'\nNDIM, \t    gives the dimensions of the data cube to be examined'
        print'FP_REP+DIM, gives choice of(1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8'
        print'\t    (1)\t\t  (2)\t\t(3)\t      (4)\n'
        sys.exit(0)

    fig = Figure()
    ax = fig.add_subplot(111)

    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
