# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Wed Mar 23 16:24:50 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(639, 379)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/callum.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(False)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Scroll = QtWidgets.QScrollBar(self.centralWidget)
        self.Scroll.setOrientation(QtCore.Qt.Vertical)
        self.Scroll.setObjectName("Scroll")
        self.horizontalLayout.addWidget(self.Scroll)
        self.mplwindow = QtWidgets.QWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplwindow.sizePolicy().hasHeightForWidth())
        self.mplwindow.setSizePolicy(sizePolicy)
        self.mplwindow.setObjectName("mplwindow")
        self.mplvl = QtWidgets.QVBoxLayout(self.mplwindow)
        self.mplvl.setContentsMargins(0, 0, 0, 0)
        self.mplvl.setObjectName("mplvl")
        self.horizontalLayout.addWidget(self.mplwindow)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, 10, 200)
        self.gridLayout.setObjectName("gridLayout")
        self.XView = QtWidgets.QRadioButton(self.centralWidget)
        self.XView.setObjectName("XView")
        self.gridLayout.addWidget(self.XView, 0, 0, 1, 2)
        self.ZView = QtWidgets.QRadioButton(self.centralWidget)
        self.ZView.setObjectName("ZView")
        self.gridLayout.addWidget(self.ZView, 2, 0, 1, 2)
        self.YView = QtWidgets.QRadioButton(self.centralWidget)
        self.YView.setObjectName("YView")
        self.gridLayout.addWidget(self.YView, 1, 0, 1, 2)
        self.Bore = QtWidgets.QToolButton(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Bore.sizePolicy().hasHeightForWidth())
        self.Bore.setSizePolicy(sizePolicy)
        self.Bore.setObjectName("Bore")
        self.gridLayout.addWidget(self.Bore, 3, 0, 1, 2)
        self.horizontalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 639, 25))
        self.menuBar.setObjectName("menuBar")
        self.menu_Menu = QtWidgets.QMenu(self.menuBar)
        self.menu_Menu.setObjectName("menu_Menu")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.Open = QtWidgets.QAction(MainWindow)
        self.Open.setObjectName("Open")
        self.menu_Menu.addAction(self.Open)
        self.menuBar.addAction(self.menu_Menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Data Cube Viewer"))
        self.XView.setText(_translate("MainWindow", "X View"))
        self.ZView.setText(_translate("MainWindow", "Z View"))
        self.YView.setText(_translate("MainWindow", "Y View"))
        self.Bore.setText(_translate("MainWindow", "Draw Bore "))
        self.menu_Menu.setTitle(_translate("MainWindow", "&Menu"))
        self.Open.setText(_translate("MainWindow", "&Open"))
        self.Open.setToolTip(_translate("MainWindow", "Open a file"))
        self.Open.setShortcut(_translate("MainWindow", "Ctrl+O"))
