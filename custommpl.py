#!/usr/bin/python
from PyQt4.uic import loadUiType

import gc
import os

from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import matplotlib.colors as colors
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
        self.ave = np.array([])         # empty array for average bore
        self.auto_flag = False          # autoscale flag
        self.spinBoxval = 0             # defualt 4D data_cube dimension
        self.spinBox.hide()             # hide option unless 4D
        self.colourmap = 'viridis'      # default colourmap
        self.interpMethod = 'nearest'   # default interp method
        self.cmapmin = None             # default colourbar range, i.e let matplotlib decide
        self.cmapmax = None
        self.hres = 1                   # default res, i.e jut voxel numbers on axis
        self.vres = 1
        self.Normx = None               # normalisation method. default set to None
        self.Normy = None
        self.Normz = None

        self.XView.setChecked(True)
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.X = np.array([])
        self.AveBoreView = 'X'

        # change view of cube
        self.XView.toggled.connect(lambda: self.btnstate(self.XView))
        self.YView.toggled.connect(lambda: self.btnstate(self.YView))
        self.ZView.toggled.connect(lambda: self.btnstate(self.ZView))
        self.Bore.toggled.connect(lambda: self.btnstate(self.Bore))
        self.AverageBore.toggled.connect(
            lambda: self.btnstate(self.AverageBore))

        # update data when slider moved
        self.Scroll_Horz.sliderMoved.connect(self.sliderval)
        self.Scroll_Vert.sliderMoved.connect(self.sliderval)

        if len(sys.argv) >= 2:
            # open file dialog if no file provided on cmd line
            self.file_open(sys.argv[1:4])
        self.Open.triggered.connect(self.file_open)
        self.Save_Avg_Bore.triggered.connect(self.saveBore)
        self.Reset.triggered.connect(self.reset_plot)
        self.AutoScale.triggered.connect(self.Auto_Scale_plot)
        # self.Bore_View.triggered.connect(self.ViewBore)
        self.action_Save_Gif.triggered.connect(self.saveGif)
        self.action_Colour_Map.triggered.connect(self.changeColourMap)
        self.action_Interpolation_Method.triggered.connect(self.changeInterpolationMethod)
        self.action_Colour_Bar_Clip.triggered.connect(self.changeclipColourBarRange)
        self.action_Save_Image.triggered.connect(self.saveImage)
        self.action_Normalisation_Method.triggered.connect(self.changeNormMethod)

        self.spinBox.valueChanged.connect(self.changeSpinbox)

    def changeNormMethod(self, ):
        # func to change Normalisation method of matshow
        method = self.getNormDialog()
        if(method == 'Log'):
            self.Normx = colors.LogNorm(vmin=0.1,
                                        vmax=self.X[self.ind, :, :].max())
            self.Normy = colors.LogNorm(vmin=0.1,
                                        vmax=self.X[:, self.ind, :].max())
            self.Normz = colors.LogNorm(vmin=0.1,
                                        vmax=self.X[:, :, self.ind].max())
        elif(method == 'Symmetric Log'):
            self.Normx = colors.SymLogNorm(linthresh=1.,
                                           vmin=self.X[self.ind, :, :].min(),
                                           vmax=self.X[self.ind, :, :].max())
            self.Normy = colors.SymLogNorm(linthresh=1.,
                                           vmin=self.X[:, self.ind, :].min(),
                                           vmax=self.X[:, self.ind, :].max())
            self.Normz = colors.SymLogNorm(linthresh=1.,
                                           vmin=self.X[:, :, self.ind].max(),
                                           vmax=self.X[:, :, self.ind].max())
        elif(method == 'Linear'):
            self.Normx = None
            self.Normy = None
            self.Normz = None
        self.reset_plot(False)
        self.init_plot()

    def saveImage(self, ):
        # saves data and image of current view
        name = self.showGifDialog()
        if self.XView.isChecked():
            np.savetxt(name + '.dat', self.X[self.Scroll_Vert.value(), :, :],
                       delimiter=' ')
        elif self.YView.isChecked():
            np.savetxt(name + '.dat', self.X[:, self.Scroll_Vert.value(), :],
                       delimiter=' ')
        elif self.ZView.isChecked():
            np.savetxt(name + '.dat', self.X[:, :, self.Scroll_Vert.value()],
                       delimiter=' ')

        self.hres, self.vres = self.showextentDialog()
        # scale x, y ticks to actual scale based upon user definition
        # thanks https://stackoverflow.com/a/17816809/6106938
        # change so that it uses extent=[xmin, xmax, ymin, ymax]
        # set default as None
        # then change here. extent added to matshow(*args, extent=[...])
        ticks = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x * self.hres))
        self.ax1.xaxis.set_major_formatter(ticks)
        ticks = ticker.FuncFormatter(lambda y, pos: '{0:g}'.format(y * self.vres))
        self.ax1.yaxis.set_major_formatter(ticks)
        self.fig.savefig(name + '.png')

    def changeColourMap(self, ):
        # change cmap
        self.colourmap = self.showColourmapsDialog()
        self.reset_plot(False)
        self.init_plot()

    def changeclipColourBarRange(self, ):
        # change vmin, vmax for cbar
        try:
            self.cmapmin, self.cmapmax = self.showclipColourBarDialog()
        except TypeError:
            pass
        self.reset_plot(False)
        self.init_plot()

    def changeInterpolationMethod(self, ):
        # change interpolation method for image
        self.interpMethod = str(self.showInterpolationDialog())
        self.reset_plot(False)
        self.init_plot()

    def is_perfect_cube(self, x):
        # shitty cheat so i dont have to enter numbers...
        x = abs(x)
        p = x ** (1. / 3)
        if int(round(p)) ** 3 == x:
            return int(round(p))
        else:
            return 0

    def saveGif(self):
        rang = self.showGifframesDialog()  # get range of frames
        step = self.showGifstepDialog()    # get number of images
        name = self.showGifDialog()        # name of file
        tight = self.showGifExtent()       # tight or not
        # loop over range and make images
        tmpplace = self.Scroll_Vert.value()
        if rang * step > tmpplace:
            rang = tmpplace
        for i in range(rang):
            self.Scroll_Horz.setValue(self.ind)
            self.Scroll_Vert.setValue(tmpplace - (i * step))
            self.sliderval()
            if tight:
                extent = self.ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
                self.fig.savefig('pic' + str(i) + '.png', bbox_inches=extent)
            else:
                self.fig.savefig('pic' + str(i) + '.png')
        # use imagemagick to create gif
        os.system('convert -delay 20 $(ls pic*.png -v) ' + name + '.gif')
        os.system('rm pic*.png')

    def changeSpinbox(self):
        # for 4d data cubes
        self.spinBoxval = int(self.spinBox.value())
        fd = open(self.name, 'rb')
        self.readslice(fd, 200, 200, 200, np.float64, 4)
        self.reset_plot()
        self.init_plot()

    def Auto_Scale_plot(self):
        # autoscale cbar on plot and reset clipping if any
        self.cmapmin = None
        self.cmapmax = None
        if not self.auto_flag:
            self.auto_flag = True
        else:
            self.auto_flag = False

    def sliderval(self):
        # move slider and update data
        try:
            if self.XView.isChecked():
                self.im.set_data(self.X[self.Scroll_Vert.value(), :, :])
            elif self.YView.isChecked():
                self.im.set_data(self.X[:, self.Scroll_Vert.value(), :])
            elif self.ZView.isChecked():
                self.im.set_data(self.X[:, :, self.Scroll_Vert.value()])
            elif self.Bore.isChecked():
                if self.BoreView == 'X':
                    self.im.set_ydata(self.X[:, self.Scroll_Horz.value(), self.Scroll_Vert.value()][::])
                elif self.BoreView == 'Y':
                    self.im.set_ydata(self.X[self.Scroll_Horz.value(), :, self.Scroll_Vert.value()][::])
                elif self.BoreView == 'Z':
                    self.im.set_ydata(self.X[self.Scroll_Vert.value(), self.Scroll_Horz.value(), :][::])
            elif self.AverageBore.isChecked():
                self.Scroll_Horz.setValue(self.ind)
                self.Scroll_Vert.setValue(self.ind)
        except IndexError:
            pass

        # try and redraw
        try:
            self.im.axes.figure.canvas.draw()
            if self.auto_flag:
                self.im.autoscale()
        except AttributeError:
            pass

    def addmpl(self):
        # add plot to anvas
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow)
        self.mplvl.addWidget(self.toolbar)

    def rmmpl(self):
        # delete plot from canvas
        try:
            self.mplvl.removeWidget(self.canvas)
            self.canvas.close()
            self.mplvl.removeWidget(self.toolbar)
            self.toolbar.close()
        except:
            pass

    def saveBore(self,):
        # save bore as a list of points
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        f = open(name, 'w')
        if len(self.ave) > 1:
            for i in range(len(self.ave)):
                f.write(str(self.ave[i]) + '\n')
            f.close()
        else:
            tmp = self.X[:, self.Scroll_Horz.value() - 1, self.Scroll_Vert.value() - 1]
            for i in range(len(tmp)):
                f.write(str(tmp[i]) + '\n')

    def file_open(self, *args):
        try:
            self.reset_plot()
        except:
            pass
        if args[0]:
            args = args[0]
            self.name = args[0]
            if len(args) == 2:
                ndim = (args[1], args[1], args[1])

                item = str(self.showDtDialog())

            elif len(args) == 3:
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
                # bug here. can be perfect cube, but not correct cube dims...
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
            self.readslice(fd, int(ndim[0]), int(
                ndim[1]), int(ndim[2]), dt, dim)
            self.init_plot()
        except ValueError:
            self.ErrorDialog("Value of Ndim incorrect for this data cube.")

    def btnstate(self, b):

        if b.text() == "X View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.im = self.ax1.matshow(self.X[self.ind, :, :],
                                           vmin=self.cmapmin, vmax=self.cmapmax,
                                           cmap=str(self.colourmap), interpolation=self.interpMethod,
                                           norm=self.Normx)
                self.fig.colorbar(self.im)
                self.fig.set_tight_layout(True)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Y View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.im = self.ax1.matshow(self.X[:, self.ind, :],
                                           vmin=self.cmapmin, vmax=self.cmapmax,
                                           cmap=str(self.colourmap), interpolation=self.interpMethod,
                                           norm=self.Normy)
                self.fig.colorbar(self.im)
                self.fig.set_tight_layout(True)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Z View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.Scroll_Vert.setMaximum(self.slices)
                self.im = self.ax1.matshow(self.X[:, :, self.ind],
                                           vmin=self.cmapmin, vmax=self.cmapmax,
                                           cmap=str(self.colourmap), interpolation=self.interpMethod,
                                           norm=self.Normz)
                self.fig.colorbar(self.im)
                self.fig.set_tight_layout(True)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Draw Bore":
            if b.isChecked() is True:
                self.ViewBore()
                self.reset_plot(False)
                if self.BoreView == 'X':
                    self.im, = self.ax1.plot(self.X[:, self.ind, self.ind])
                elif self.BoreView == 'Y':
                    self.im, = self.ax1.plot(self.X[self.ind, :, self.ind])
                elif self.BoreView == 'Z':
                    self.im, = self.ax1.plot(self.X[self.ind, self.ind, :])
                self.fig.set_tight_layout(True)
                self.addmpl()

        if b.text() == "Avg. Bore":
            if b.isChecked() is True:
                self.AveBoreChecked()

    def ViewBore(self):
        self.BoreView = self.showBoreViewDialog()
        if self.BoreView == 'X':
            self.view = (1, 2)
        elif self.BoreView == 'Y':
            self.view = (0, 2)
        elif self.BoreView == 'Z':
            self.view = (0, 1)

    def AveBoreChecked(self):

        self.ViewBore()

        self.reset_plot(False)
        if len(self.ave) == 0:
            self.ave = np.array([])
            self.ave = np.sum(self.X, self.view)
            self.ave /= (len(self.X[self.view[0]]) * len(self.X[self.view[1]]))

        self.im = self.ax1.plot(self.ave[::])
        self.fig.set_tight_layout(True)
        self.addmpl()

    def reset_plot(self, *args):
        self.ave = np.array([])

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

        rows, cols, self.slices = self.X.shape
        self.ind = int(rows / 2)
        if self.XView.isChecked():
            view = self.XView
            self.Scroll_Vert.setMaximum(rows)
        elif self.YView.isChecked():
            view = self.YView
            self.Scroll_Vert.setMaximum(cols)
        elif self.ZView.isChecked():
            view = self.ZView
            self.Scroll_Vert.setMaximum(self.slices)
        elif self.AverageBore.isChecked():
            view = self.AverageBore
            self.Scroll_Vert.setMaximum(self.slices)
        elif self.Bore_View.isChecked():
            view = self.ViewBore
            self.Scroll_Vert.setMaximum(self.slices)
        self.btnstate(view)
        self.Scroll_Horz.setMaximum(self.slices)
        self.Scroll_Horz.setValue(self.ind)
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

    def showBoreViewDialog(self, ):
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

    def showextentDialog(self, ):
        hres, ok = QtGui.QInputDialog.getDouble(
            self, 'Data Extent', 'Enter horizontal resolution:', 0, -100, 100, 9,)
        if ok:
            vres, ok = QtGui.QInputDialog.getDouble(
                self, 'Data Extent', 'Enter vertical resolution:', 0, -100, 100, 9,)
            if ok:
                return (hres, vres)

    def getNormDialog(self, ):
        items = ("Log", "Linear", "Symmetric Log")

        item, ok = QtGui.QInputDialog.getItem(self, "Select cbar normalisation method",
                                              "Method:", items, 0, False)
        if ok and item:
            return item

    def showColourmapsDialog(self, ):
        items = ('viridis', 'inferno', 'plasma', 'magma', 'Blues', 'BuGn',
                 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu',
                 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
                 'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'bone', 'cool',
                 'copper', 'gist_heat', 'gray', 'hot', 'pink', 'spring',
                 'summer', 'winter', 'BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn',
                 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                 'seismic', 'Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2',
                 'Set1', 'Set2', 'Set3', 'Vega10', 'Vega20', 'Vega20b',
                 'Vega20c', 'gist_earth', 'terrain', 'ocean', 'gist_stern',
                 'brg', 'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2',
                 'gist_ncar', 'nipy_spectral', 'jet', 'rainbow', 'gist_rainbow',
                 'hsv', 'flag', 'prism')
        item, ok = QtGui.QInputDialog.getItem(self, "Select Colour Map",
                                              "Cmaps", items, 0, False)
        if ok and item:
            return item

    def showInterpolationDialog(self, ):
        items = ('none', 'nearest', 'bilinear', 'bicubic', 'spline16',
                 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
                 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell',
                 'sinc', 'lanczos')
        item, ok = QtGui.QInputDialog.getItem(self, "Select Interpolation Method",
                                              "Methods", items, 0, False)
        if ok and item:
            return item

    def showclipColourBarDialog(self, ):
        text1, ok1 = QtGui.QInputDialog.getInt(
            self, 'Input cbar min', 'Enter min:')
        if ok1:
            text2, ok2 = QtGui.QInputDialog.getInt(
                self, 'Input cbar max', 'Enter max:')
            if ok2:
                return (int(text1), int(text2))

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
