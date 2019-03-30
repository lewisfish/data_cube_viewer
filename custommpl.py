#!/home/lewis/anaconda3/bin/python
from PyQt5.uic import loadUiType

import gc
import os

from cubeclass import datacube

from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import matplotlib.colors as colors
from matplotlib.backends.backend_qt5agg import (
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
        self.X = datacube()
        self.AveBoreView = 'X'

        # change view of cube
        self.XView.toggled.connect(lambda: self.btnstate(self.XView))
        self.YView.toggled.connect(lambda: self.btnstate(self.YView))
        self.ZView.toggled.connect(lambda: self.btnstate(self.ZView))
        self.Bore.toggled.connect(lambda: self.btnstate(self.Bore))
        self.AverageBore.toggled.connect(
            lambda: self.btnstate(self.AverageBore))

        # update data when slider moved
        self.Scroll_Horz.valueChanged[int].connect(self.sliderval)
        self.Scroll_Vert.valueChanged[int].connect(self.sliderval)

        self.file_open(args)
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
        self.action_Bore_Location.triggered.connect(self.setBoreLocation)

        self.spinBox.valueChanged.connect(self.changeSpinbox)

    def setBoreLocation(self, ):

        xloc, ok = QtWidgets.QInputDialog.getInt(
            self, 'Input location', 'Enter X location:')

        yloc, ok = QtWidgets.QInputDialog.getInt(
            self, 'Input location', 'Enter Y location:')

        self.Scroll_Horz.setValue(xloc)
        self.Scroll_Vert.setValue(yloc)

        if self.Bore.isChecked():
            if self.BoreView == 'X':
                self.im.set_ydata(self.X.data[:, xloc, yloc][::])
            elif self.BoreView == 'Y':
                self.im.set_ydata(self.X.data[xloc, :, yloc][::])
            elif self.BoreView == 'Z':
                self.im.set_ydata(self.X.data[yloc, xloc, :][::])

        # try and redraw
        try:
            self.im.axes.figure.canvas.draw()
            if self.auto_flag:
                self.im.autoscale()
        except AttributeError:
            pass

    def changeNormMethod(self, ):
        # func to change Normalisation method of matshow
        method = self.getNormDialog()
        if(method == 'Log'):
            self.Normx = colors.LogNorm(vmin=0.1,
                                        vmax=self.X.data[self.ind, :, :].max())
            self.Normy = colors.LogNorm(vmin=0.1,
                                        vmax=self.X.data[:, self.ind, :].max())
            self.Normz = colors.LogNorm(vmin=0.1,
                                        vmax=self.X.data[:, :, self.ind].max())
        elif(method == 'Symmetric Log'):
            self.Normx = colors.SymLogNorm(linthresh=1.,
                                           vmin=self.X.data[self.ind, :, :].min(),
                                           vmax=self.X.data[self.ind, :, :].max())
            self.Normy = colors.SymLogNorm(linthresh=1.,
                                           vmin=self.X.data[:, self.ind, :].min(),
                                           vmax=self.X.data[:, self.ind, :].max())
            self.Normz = colors.SymLogNorm(linthresh=1.,
                                           vmin=self.X.data[:, :, self.ind].max(),
                                           vmax=self.X.data[:, :, self.ind].max())
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
            np.savetxt(name + '.dat', self.X.data[self.Scroll_Vert.value(), :, :],
                       delimiter=' ')
        elif self.YView.isChecked():
            np.savetxt(name + '.dat', self.X.data[:, self.Scroll_Vert.value(), :],
                       delimiter=' ')
        elif self.ZView.isChecked():
            np.savetxt(name + '.dat', self.X.data[:, :, self.Scroll_Vert.value()],
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

        self.cmapmin, self.cmapmax = self.showclipColourBarDialog()

        self.reset_plot(False)
        self.init_plot()

    def changeInterpolationMethod(self, ):
        # change interpolation method for image
        self.interpMethod = str(self.showInterpolationDialog())
        self.reset_plot(False)
        self.init_plot()

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
                self.fig.savefig(str(i).zfill(3) + 'pic.png', bbox_inches=extent)
            else:
                self.fig.savefig(str(i).zfill(3) + 'pic.png')
        # use ffmpeg to create gif
        if tight:
            os.system("mogrify -trim *pic.png")
        os.system("ffmpeg -framerate 10 -pattern_type glob -i '*pic.png' -c:v libx264 -r 24 -pix_fmt yuv420p -vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' " + name + ".mp4")
        os.system('rm *pic.png')
        print('done')

    def changeSpinbox(self):
        # for 4d data cubes
        self.spinBoxval = int(self.spinBox.value())
        fd = open(self.name, 'rb')
        self.readslice(fd, self.ndim, np.float64, self.cubeorder)
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
        if self.XView.isChecked():
            # fd = open(self.name, 'rb')
            self.X.readslice(self.Scroll_Horz.value())
            self.im.set_data(self.X.data[self.Scroll_Vert.value(), :, :])
            # self.Scroll_Horz.setValue(0)  # pin unsed slider
        elif self.YView.isChecked():
            self.X.readslice(self.Scroll_Horz.value())
            self.im.set_data(self.X.data[:, self.Scroll_Vert.value(), :])
            # self.Scroll_Horz.setValue(0)  # pin unsed slider
        elif self.ZView.isChecked():
            self.X.readslice(self.Scroll_Horz.value())
            self.im.set_data(self.X.data[:, :, self.Scroll_Vert.value()])
            # self.Scroll_Horz.setValue(0)  # pin unsed slider
        elif self.Bore.isChecked():
            if self.BoreView == 'X':
                self.im.set_ydata(self.X.data[:, self.Scroll_Horz.value(), self.Scroll_Vert.value()][::])
                if self.auto_flag:
                    self.ax1.relim()
                    self.ax1.autoscale_view(True, True, True)
            elif self.BoreView == 'Y':
                self.im.set_ydata(self.X.data[self.Scroll_Horz.value(), :, self.Scroll_Vert.value()][::])
                if self.auto_flag:
                    self.ax1.relim()
                    self.ax1.autoscale_view(True, True, True)
            elif self.BoreView == 'Z':
                self.im.set_ydata(self.X.data[self.Scroll_Vert.value(), self.Scroll_Horz.value(), :][::])
                if self.auto_flag:
                    self.ax1.relim()
                    self.ax1.autoscale_view(True, True, True)
        elif self.AverageBore.isChecked():
            self.Scroll_Horz.setValue(self.ind)
            self.Scroll_Vert.setValue(self.ind)

        # try and redraw
        try:
            self.im.axes.figure.canvas.draw()
            if self.auto_flag:
                self.im.autoscale()
        except AttributeError:
            pass

    def addmpl(self):
        # add plot to anvas
        self.rmmpl()
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow)
        self.mplvl.addWidget(self.toolbar)

    def rmmpl(self):
        # delete plot from canvas
        try:
            self.canvas.close()
            self.canvas.deleteLater()
            self.toolbar.close()
            self.toolbar.deleteLater()
            gc.collect()
        except:
            pass

    def saveBore(self,):
        # save bore as a list of points
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        f = open(name, 'w')
        if len(self.ave) > 1:
            for i in range(len(self.ave)):
                f.write(str(self.ave[i]) + '\n')
            f.close()
        else:
            if self.BoreView == "X":
                tmp = self.X[:, self.Scroll_Horz.value(), self.Scroll_Vert.value()]
            elif self.BoreView == "Y":
                tmp = self.X[self.Scroll_Horz.value(), :, self.Scroll_Vert.value()]
            elif self.BoreView == "Z":
                tmp = self.X[self.Scroll_Horz.value(), self.Scroll_Vert.value(), :]

            for i in range(len(tmp)):
                f.write(str(tmp[i]) + '\n')

    def file_open(self, args):

        self.reset_plot()

        while True:
            try:
                # get file name
                if args.file is None:
                    self.X.name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')[0]
                else:
                    self.X.name = args.file

                # get precision of data cube
                self.X.dtype, self.X.cubeorder, item = self.getPrec(args)

                # get dimensions of data cube. can be guessed
                bool4d = False
                if self.X.cubeorder == 4:
                    bool4d = True
                self.X.ndim = self.getSize(args, item, bool4d)

                try:
                    fd = open(self.X.name, 'rb')
                except FileNotFoundError:
                    self.ErrorDialog("File not Found!")
                    self.name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')[0]

                self.X.readslice(0)
                self.init_plot()
                break
            # except ValueError:
            #     self.ErrorDialog("Value of Ndim incorrect for this data cube.")
            #     args.ndim = None
            #     args.fpprec = None
            except UnboundLocalError:
                pass
                break

    def getSize(self, args, item, bool4d):
        if args.ndim is None and item:
            size = os.path.getsize(self.X.name)
            if "Real*8" in item:
                size /= 8
            elif "Real*4" in item:
                size /= 4
            if self.X.is_perfect_cube(size) != 0:
                size = self.X.is_perfect_cube(size)
                ndim = (size, size, size)
            else:
                ndim = self.showNdimDialog(bool4d)
        else:
            ndim = (args.ndim, args.ndim, args.ndim)

        return ndim

    def getPrec(self, args):
        # get precision of data cube
        item = None
        if args.fpprec is None:
            item = str(self.showDtDialog())
            if "Real*8" in item:
                dt = np.float64
            elif "Real*4" in item:
                dt = np.float32

            if "4 dim" in item:
                dim = 4
            elif "3 dim" in item:
                dim = 3
        else:
            if args.fpprec == 1:
                dt = np.float32
                dim = 4
            elif args.fpprec == 2:
                dt = np.float64
                dim = 4
            elif args.fpprec == 3:
                dt = np.float32
                dim = 3
            elif args.fpprec == 4:
                dt = np.float64
                dim = 3
        return dt, dim, item

    def btnstate(self, b):

        if b.text() == "X View":
            if b.isChecked() is True:
                self.reset_plot(False)
                self.Scroll_Vert.setMaximum(self.rows - 1)
                self.im = self.ax1.matshow(self.X.data[self.ind, :, :],
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
                self.Scroll_Vert.setMaximum(self.cols - 1)
                self.im = self.ax1.matshow(self.X.data[:, self.ind, :],
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
                self.Scroll_Vert.setMaximum(self.slices - 1)
                self.im = self.ax1.matshow(self.X.data[:, :, self.ind],
                                           vmin=self.cmapmin, vmax=self.cmapmax,
                                           cmap=str(self.colourmap), interpolation=self.interpMethod,
                                           norm=self.Normz)
                try:
                    self.fig.colorbar(self.im)
                except ZeroDivisionError:
                    self.ErrorDialog("Divison by zero, try another range")
                    self.Normz = None
                    self.Normy = None
                    self.Normz = None
                    self.cmapmin = None
                    self.cmapmax = None
                    self.btnstate(b)
                self.fig.set_tight_layout(True)
                self.ax1.set_aspect('auto')
                self.addmpl()

        if b.text() == "Draw Bore":
            if b.isChecked() is True:
                self.ViewBore()
                self.reset_plot(False)
                if self.BoreView == 'X':
                    self.im, = self.ax1.plot(self.X.data[:, self.ind, self.ind])
                elif self.BoreView == 'Y':
                    self.im, = self.ax1.plot(self.X.data[self.ind, :, self.ind])
                elif self.BoreView == 'Z':
                    self.im, = self.ax1.plot(self.X.data[self.ind, self.ind, :])
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
            self.ave = np.sum(self.X.data, self.view)
            self.ave /= (len(self.X.data[self.view[0]]) * len(self.X.data[self.view[1]]))

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
        self.rmmpl()

    def init_plot(self, ):

        self.rmmpl()

        self.rows, self.cols, self.slices, self.depth = self.X.ndim
        self.ind = 0  # int(rows / 2)
        if self.XView.isChecked():
            view = self.XView
            self.Scroll_Vert.setMaximum(self.rows)
            self.Scroll_Horz.setMaximum(self.depth)
        elif self.YView.isChecked():
            view = self.YView
            self.Scroll_Vert.setMaximum(self.cols)
            self.Scroll_Horz.setMaximum(self.depth)
        elif self.ZView.isChecked():
            view = self.ZView
            self.Scroll_Vert.setMaximum(self.slices)
            self.Scroll_Horz.setMaximum(self.cols)
        elif self.AverageBore.isChecked():
            view = self.AverageBore
            self.Scroll_Vert.setMaximum(self.rows)
        elif self.Bore_View.isChecked():
            view = self.ViewBore
            self.Scroll_Vert.setMaximum(self.cols)
            self.Scroll_Horz.setMaximum(self.rows)
        self.btnstate(view)
        self.Scroll_Horz.setValue(self.ind)
        self.Scroll_Vert.setValue(self.ind)

    def showGifframesDialog(self, ):
        text, ok = QtWidgets.QInputDialog.getInt(
            self, '# of frames', 'Enter # of frames:')
        if ok:
            return(text)

    def showGifstepDialog(self, ):
        text, ok = QtWidgets.QInputDialog.getInt(
            self, 'Step size', 'Enter value of step:')
        if ok:
            return(text)

    def showGifExtent(self, ):
        items = ("Colour Bar", "No Colour Bar")

        text, ok = QtWidgets.QInputDialog.getItem(
            self, "Colour Bar on GIF?", " ", items, 0, False)

        if ok and text:
            if items == "Colour Bar":
                text = False
            else:
                text = True
            return text

    def showNdimDialog(self, bool4d):
        text1, ok1 = QtWidgets.QInputDialog.getInt(
            self, 'Input Ndim', 'Enter X Ndim:')
        if ok1:
            text2, ok2 = QtWidgets.QInputDialog.getInt(
                self, 'Input Ndim', 'Enter Y Ndim:')
            if ok2:
                text3, ok3 = QtWidgets.QInputDialog.getInt(
                    self, 'Input Ndim', 'Enter Z Ndim:')
                if ok3 and bool4d:
                    text4, ok4 = QtWidgets.QInputDialog.getInt(
                        self, 'Input Ndim', 'Enter T Ndim:')
                    return (text1, text2, text3, text4)
                else:
                    return (text1, text2, text3)

    def showDtDialog(self, ):
        items = ("4 dim Real*4", "4 dim Real*8",
                 "3 dim Real*4", "3 dim Real*8")

        item, ok = QtWidgets.QInputDialog.getItem(self, "Select Fortran Precision",
                                                  "Precisions", items, 0, False)

        if ok and item:
            return item

    def showBoreViewDialog(self, ):
        items = ("X", "Y", "Z")
        item, ok = QtWidgets.QInputDialog.getItem(self, "Select Average Bore Direction",
                                                  "Views", items, 0, False)
        if ok and item:
            return item

    def showGifDialog(self, ):
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'Filename Dialog', 'Enter filename:')
        if ok:
            return str(text)

    def showextentDialog(self, ):
        hres, ok = QtWidgets.QInputDialog.getDouble(
            self, 'Data Extent', 'Enter horizontal resolution:', 0, -100, 100, 9,)
        if ok:
            vres, ok = QtWidgets.QInputDialog.getDouble(
                self, 'Data Extent', 'Enter vertical resolution:', 0, -100, 100, 9,)
            if ok:
                return (hres, vres)

    def getNormDialog(self, ):
        items = ("Log", "Linear", "Symmetric Log")

        item, ok = QtWidgets.QInputDialog.getItem(self, "Select cbar normalisation method",
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
        item, ok = QtWidgets.QInputDialog.getItem(self, "Select Colour Map",
                                                  "Cmaps", items, 0, False)
        if ok and item:
            return item

    def showInterpolationDialog(self, ):
        items = ('none', 'nearest', 'bilinear', 'bicubic', 'spline16',
                 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
                 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell',
                 'sinc', 'lanczos')
        item, ok = QtWidgets.QInputDialog.getItem(self, "Select Interpolation Method",
                                                  "Methods", items, 0, False)
        if ok and item:
            return item

    def showclipColourBarDialog(self, ):
        text1, ok1 = QtWidgets.QInputDialog.getDouble(
            self, 'Input cbar min', 'Enter min:')
        if ok1:
            text2, ok2 = QtWidgets.QInputDialog.getDouble(
                self, 'Input cbar max', 'Enter max:')
            if ok2:
                return (int(text1), int(text2))

    def ErrorDialog(self, ErrMsg):
        QtWidgets.QMessageBox.warning(self, "Error", ErrMsg)


if __name__ == '__main__':
    import sys
    from PyQt5 import QtCore, QtWidgets, QtGui
    import numpy as np
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-f", "--file", type=str,
                        help="Name of file to be plotted.")
    parser.add_argument("-n", "--ndim", type=int,
                        help="Gives the dimensions of the data cube to be examined.")
    parser.add_argument("-d", "--fpprec", type=int, choices=[1, 2, 3, 4],
                        help="Gives choice of (1-4):\n\n\t4 dim Real*4, 4 dim Real*8, 3 dim Real*4, 3 dim Real*8.")

    args = parser.parse_args()

    fig = Figure()
    ax = fig.add_subplot(111)

    app = QtWidgets.QApplication([])
    main = Main()
    main.show()
    sys.exit(app.exec_())
