#!/usr/bin/python
from PyQt4.uic import loadUiType

import gc
import os

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

path = os.path.abspath(os.path.dirname(__file__))
Ui_MainWindow, QMainWindow = loadUiType(path + '/mainwindow.ui')


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.showMaximized()
        self.flag = 0
        self.ave = np.array([])
        self.auto_flag = False
        self.spinBoxval = 0
        self.spinBox.hide()
        self.colourmap = 'viridis'
        self.interpMethod = 'nearest'

        self.XView.setChecked(True)
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.X = np.array([])
        self.AveBoreView = 'X'

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
        self.Save_Avg_Bore.triggered.connect(self.saveBore)
        self.Reset.triggered.connect(self.reset_plot)
        self.AutoScale.triggered.connect(self.Auto_Scale_plot)
        self.Bore_View.triggered.connect(self.ViewBore)
        self.action_Save_Gif.triggered.connect(self.saveGif)
        self.action_Colour_Map.triggered.connect(self.changeColourMap)
        self.action_Interpolation_Method.triggered.connect(self.changeInterpolationDialog)

        self.spinBox.valueChanged.connect(self.changeSpinbox)

    def changeColourMap(self, ):
        self.colourmap = self.showColourmapsDialog()
        self.reset_plot(False)
        self.init_plot()

    def changeInterpolationDialog(self, ):
        self.interpMethod = str(self.showInterpolationDialog())
        self.reset_plot(False)
        self.init_plot()

    def is_perfect_cube(self, x):
        x = abs(x)
        p = x ** (1. / 3)
        if int(round(p)) ** 3 == x:
            return int(round(p))
        else:
            return 0

    def saveGif(self):
        rang = self.showGifframesDialog()
        step = self.showGifstepDialog()
        name = self.showGifDialog()
        tight = self.showGifExtent()
        for i in range(rang):
            self.Scroll_Horz.setValue(self.ind)
            self.Scroll_Vert.setValue(rang - (i * step))
            self.sliderval()
            if tight:
                extent = self.ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
                self.fig.savefig('pic' + str(i) + '.png', bbox_inches=extent)
            else:
                self.fig.savefig('pic' + str(i) + '.png')
        os.system('convert -delay 20 $(ls pic*.png -v) ' + name + '.gif')
        os.system('rm pic*.png')

    def changeSpinbox(self):
        self.spinBoxval = int(self.spinBox.value())
        fd = open(self.name, 'rb')
        self.readslice(fd, 200, 200, 200, np.float64, 4)
        self.reset_plot()
        self.init_plot()

    def ViewBore(self):
        self.AveBoreView = self.showBvDialog()
        self.AverageBore.setChecked(True)
        self.BoreChecked()

    def Auto_Scale_plot(self):
        if not self.auto_flag:
            self.auto_flag = True
        else:
            self.auto_flag = False

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
                    self.X[:, self.Scroll_Horz.value(), self.Scroll_Vert.value()][::])
            elif self.AverageBore.isChecked():
                self.Scroll_Horz.setValue(self.ind)
                self.Scroll_Vert.setValue(self.ind)
        except IndexError:
            pass

        try:
            self.im.axes.figure.canvas.draw()
            if self.auto_flag:
                self.im.autoscale()
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
        try:
            self.mplvl.removeWidget(self.canvas)
            self.canvas.close()
            self.mplvl.removeWidget(self.toolbar)
            self.toolbar.close()
        except:
            pass
        # self.im.autoscale()

    def saveBore(self,):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        f = open(name, 'w')
        if len(self.ave) > 1:
            for i in range(len(self.ave)):
                f.write(str(self.ave[i]) + '\n')
            f.close()
        else:
            tmp = self.X[:, self.ind, self.ind]
            for i in range(len(tmp)):
                f.write(str(tmp[i]) + '\n')

    def file_open(self, *args):
        if self.flag == 1:
            self.reset_plot()
        try:
            self.reset_plot()
        except:
            pass
        if args[0]:
            args = args[0]
            self.name = args[0]
            if len(args) == 2:
                # ndim = args[1]
                ndim = (args[1], args[1], args[1])

                item = str(self.showDtDialog())

            elif len(args) == 3:
                # ndim = args[1]
                ndim = (args[1], args[1], args[1])
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
                item = str(self.showDtDialog())
                size = os.path.getsize(self.name)
                if "Real*8" in item:
                    if size % 8 == 0:
                        size /= 8
                elif "Real*4" in item:
                    if size % 4 == 0:
                        size /= 4

                if self.is_perfect_cube(size) != 0:
                    size = self.is_perfect_cube(size)
                    ndim = (size, size, size)
                else:
                    ndim = self.showNdimDialog()

            args = None
        else:
            self.name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
            ndim = self.showNdimDialog()
            item = str(self.showDtDialog())

        if "Real*8" in item:
            dt = np.float64
        elif "Real*4" in item:
            dt = np.float32

        if "4 dim" in item:
            dim = 4
            self.spinBox.show()
        elif "3 dim" in item:
            dim = 3

        try:
            fd = open(self.name, 'rb')
        except IOError:
            pass
        try:
            # del self.X
            self.readslice(fd, int(ndim[0]), int(
                ndim[1]), int(ndim[2]), dt, dim)
            self.init_plot()
        except ValueError:
            self.ErrorDialog("Value of Ndim incorrect for this data cube.")
            # self.rmmpl()

    def btnstate(self, b):

        if b.text() == "X View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.im = self.ax1.matshow(self.X[self.ind, :, :],
                                           cmap=str(self.colourmap), interpolation=self.interpMethod)
                self.fig.colorbar(self.im)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Y View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.im = self.ax1.matshow(
                    self.X[:, self.ind, :], cmap=str(self.colourmap), interpolation=self.interpMethod)
                self.fig.colorbar(self.im)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Z View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.im = self.ax1.matshow(
                    self.X[:, :, self.ind], cmap=str(self.colourmap), interpolation=self.interpMethod)
                self.fig.colorbar(self.im)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Draw Bore":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.im, = self.ax1.plot(self.X[:, self.ind, self.ind])
                self.addmpl()

        if b.text() == "Avg. Bore":
            if b.isChecked() is True:
                self.BoreChecked()

    def BoreChecked(self):
        if self.AveBoreView == 'X':
            self.view = (1, 2)
        elif self.AveBoreView == 'Y':
            self.view = (0, 2)
        elif self.AveBoreView == 'Z':
            self.view = (0, 1)
        self.reset_plot(False)

        if len(self.ave) == 0:
            self.ave = np.array([])
            self.ave = np.sum(self.X, self.view)
            self.ave /= (len(self.X[self.view[0]]) * len(self.X[self.view[1]]))

        self.im = self.ax1.plot(self.ave[::])
        self.addmpl()

    def reset_plot(self, *args):
        self.ave = np.array([])
        # if args:
        #     if not args[0]:
        #         self.X = None
        self.fig.clf()
        self.ax1.clear()
        gc.collect()  # fixes most of memory leak

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
        try:
            self.rmmpl()
        except:
            pass
        # self.XView.setChecked(True)
        rows, cols, self.slices = self.X.shape
        self.ind = int(rows / 2)
        if self.XView.isChecked():
            view = self.XView
        elif self.YView.isChecked():
            view = self.YView
        elif self.ZView.isChecked():
            view = self.ZView
        elif self.AverageBore.isChecked():
            view = self.AverageBore
        elif self.Bore_View.isChecked():
            view = self.ViewBore
        self.btnstate(view)
        self.Scroll_Horz.setMaximum(self.slices)
        self.Scroll_Horz.setValue(self.ind)
        self.Scroll_Vert.setMaximum(self.slices)
        self.Scroll_Vert.setValue(self.ind)

    def readslice(self, fd, dimx, dimy, dimz, dt, dim):
        if dim == 4:
            if dt == np.float64:
                # !this sometimes needs changed try powers of 2...
                magic = 4
            elif dt == np.float32:
                magic = 4
            shape = (dimx, dimy, dimz, magic)
        elif dim == 3:
            shape = (dimx, dimy, dimz)
        data = np.fromfile(
            file=fd, dtype=dt, sep="")
        # print len(data)
        data = data.reshape(shape, order='F')
        fd.close()
        if dim == 4:
            data = data[:, :, :, self.spinBoxval]
        self.X = data[:, :, :]
        del data

    def showGifframesDialog(self, ):
        text, ok = QtGui.QInputDialog.getInt(
            self, '# of frames', 'Enter # of frames:')
        if ok:
            return(text)

    def showGifstepDialog(self, ):
        text, ok = QtGui.QInputDialog.getInt(
            self, 'Step size', 'Enter value of step:')
        if ok:
            return(text)

    def showGifExtent(self, ):
        items = ("Colour Bar", "No Colour Bar")

        text, ok = QtGui.QInputDialog.getItem(
            self, "Colour Bar on GIF?", " ", items, 0, False)

        if ok and text:
            if items == "Colour Bar":
                text = False
            else:
                text = True
            return text

    def showNdimDialog(self, ):
        text1, ok1 = QtGui.QInputDialog.getInt(
            self, 'Input Ndim', 'Enter Ndim:')
        if ok1:
            text2, ok2 = QtGui.QInputDialog.getInt(
                self, 'Input Ndim', 'Enter Ndim:')
            if ok2:
                text3, ok3 = QtGui.QInputDialog.getInt(
                    self, 'Input Ndim', 'Enter Ndim:')
                if ok3:
                    return (text1, text2, text3)

    def showDtDialog(self, ):
        items = ("4 dim Real*4", "4 dim Real*8",
                 "3 dim Real*4", "3 dim Real*8")

        item, ok = QtGui.QInputDialog.getItem(self, "Select Fortran Precision",
                                              "Precisions", items, 0, False)

        if ok and item:
            return item

    def showBvDialog(self, ):
        items = ("X", "Y", "Z")
        item, ok = QtGui.QInputDialog.getItem(self, "Select Average Bore Direction",
                                              "Views", items, 0, False)
        if ok and item:
            return item

    def showGifDialog(self, ):
        text, ok = QtGui.QInputDialog.getText(
            self, 'Filename Dialog', 'Enter filename:')
        if ok:
            return str(text)

    def showColourmapsDialog(self, ):
        items = ('viridis', 'inferno', 'plasma', 'magma', 'Blues', 'BuGn', 'BuPu',
                 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
                 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'afmhot',
                 'autumn', 'bone', 'cool', 'copper', 'gist_heat', 'gray', 'hot', 'pink',
                 'spring', 'summer', 'winter', 'BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn',
                 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic', 'Accent',
                 'Dark2', 'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3', 'Vega10',
                 'Vega20', 'Vega20b', 'Vega20c', 'gist_earth', 'terrain', 'ocean', 'gist_stern',
                 'brg', 'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2', 'gist_ncar',
                 'nipy_spectral', 'jet', 'rainbow', 'gist_rainbow', 'hsv', 'flag', 'prism')
        item, ok = QtGui.QInputDialog.getItem(self, "Select Colour Map",
                                              "Cmaps", items, 0, False)
        if ok and item:
            return item

    def showInterpolationDialog(self, ):
        items = ('none', 'nearest', 'bilinear', 'bicubic', 'spline16', 'spline36', 'hanning',
                 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel',
                 'mitchell', 'sinc', 'lanczos')
        item, ok = QtGui.QInputDialog.getItem(self, "Select Interpolation Method",
                                              "Methods", items, 0, False)
        if ok and item:
            return item

    def ErrorDialog(self, ErrMsg):
        QtGui.QMessageBox.warning(self, "Error", ErrMsg)


if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np

    if len(sys.argv) >= 2:
        if 'help' in str(sys.argv[1]) or str(sys.argv[1]) == '-h':
            print('\nUsage: d3v [FILE] [NDIM] [FP_REP+DIM](1-4)')

            print('\nNDIM, \t    gives the dimensions of the data cube to be examined')
            print(
                'FP_REP+DIM, gives choice of(1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8')
            print('\t    (1)\t\t  (2)\t\t(3)\t      (4)\n')
            sys.exit(0)

        elif len(sys.argv) < 3 and len(sys.argv) > 2:
            print('\nUsage: d3v [FILE] [NDIM] [FP_REP+DIM](1-4)')

            print('\nNDIM, \t    gives the dimensions of the data cube to be examined')
            print(
                'FP_REP+DIM, gives choice of(1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8')
            print('\t    (1)\t\t  (2)\t\t(3)\t      (4)\n')
            sys.exit(0)
    else:
        print('\nUsage: d3v [FILE] [NDIM] [FP_REP+DIM](1-4)')

        print('\nNDIM, \t    gives the dimensions of the data cube to be examined')
        print('FP_REP+DIM, gives choice of(1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8')
        print('\t    (1)\t\t  (2)\t\t(3)\t      (4)\n')
        sys.exit(0)

    fig = Figure()
    ax = fig.add_subplot(111)

    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
