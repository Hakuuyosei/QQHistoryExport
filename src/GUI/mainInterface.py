# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/GUI/maininterface.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(693, 739)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.parseConfigContainer = QtWidgets.QGroupBox(self.centralwidget)
        self.parseConfigContainer.setGeometry(QtCore.QRect(0, 0, 391, 621))
        self.parseConfigContainer.setCheckable(False)
        self.parseConfigContainer.setObjectName("parseConfigContainer")
        self.findFilesModeRadioButton1 = QtWidgets.QRadioButton(self.parseConfigContainer)
        self.findFilesModeRadioButton1.setGeometry(QtCore.QRect(10, 20, 369, 16))
        self.findFilesModeRadioButton1.setChecked(True)
        self.findFilesModeRadioButton1.setObjectName("findFilesModeRadioButton1")
        self.findFilesModeRadioButton2 = QtWidgets.QRadioButton(self.parseConfigContainer)
        self.findFilesModeRadioButton2.setGeometry(QtCore.QRect(10, 100, 369, 16))
        self.findFilesModeRadioButton2.setChecked(False)
        self.findFilesModeRadioButton2.setObjectName("findFilesModeRadioButton2")
        self.label_8 = QtWidgets.QLabel(self.parseConfigContainer)
        self.label_8.setGeometry(QtCore.QRect(10, 310, 161, 16))
        self.label_8.setObjectName("label_8")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.parseConfigContainer)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 330, 371, 283))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_18 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_3.addWidget(self.label_18, 4, 1, 1, 1)
        self.QQemojiVerCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.QQemojiVerCheckBox.setEnabled(True)
        self.QQemojiVerCheckBox.setText("")
        self.QQemojiVerCheckBox.setChecked(True)
        self.QQemojiVerCheckBox.setTristate(False)
        self.QQemojiVerCheckBox.setObjectName("QQemojiVerCheckBox")
        self.gridLayout_3.addWidget(self.QQemojiVerCheckBox, 4, 0, 1, 1)
        self.targetQQInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.targetQQInputBox.setObjectName("targetQQInputBox")
        self.gridLayout_3.addWidget(self.targetQQInputBox, 1, 2, 1, 2)
        self.label_19 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.gridLayout_3.addWidget(self.label_19, 9, 1, 1, 1)
        self.useImageCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.useImageCheckBox.setEnabled(True)
        self.useImageCheckBox.setText("")
        self.useImageCheckBox.setChecked(False)
        self.useImageCheckBox.setTristate(False)
        self.useImageCheckBox.setObjectName("useImageCheckBox")
        self.gridLayout_3.addWidget(self.useImageCheckBox, 5, 0, 1, 1)
        self.modeSelectContainer_2 = QtWidgets.QWidget(self.gridLayoutWidget_3)
        self.modeSelectContainer_2.setObjectName("modeSelectContainer_2")
        self.qqEmojiVerRadioButton1 = QtWidgets.QRadioButton(self.modeSelectContainer_2)
        self.qqEmojiVerRadioButton1.setGeometry(QtCore.QRect(10, 0, 51, 16))
        self.qqEmojiVerRadioButton1.setObjectName("qqEmojiVerRadioButton1")
        self.qqEmojiVerRadioButton2 = QtWidgets.QRadioButton(self.modeSelectContainer_2)
        self.qqEmojiVerRadioButton2.setGeometry(QtCore.QRect(90, 0, 75, 16))
        self.qqEmojiVerRadioButton2.setChecked(True)
        self.qqEmojiVerRadioButton2.setObjectName("qqEmojiVerRadioButton2")
        self.gridLayout_3.addWidget(self.modeSelectContainer_2, 4, 2, 1, 2)
        self.needMarketFaceCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.needMarketFaceCheckBox.setEnabled(True)
        self.needMarketFaceCheckBox.setText("")
        self.needMarketFaceCheckBox.setChecked(True)
        self.needMarketFaceCheckBox.setTristate(False)
        self.needMarketFaceCheckBox.setObjectName("needMarketFaceCheckBox")
        self.gridLayout_3.addWidget(self.needMarketFaceCheckBox, 11, 0, 1, 1)
        self.chatimgPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.chatimgPathSelectButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.chatimgPathSelectButton.setFont(font)
        self.chatimgPathSelectButton.setObjectName("chatimgPathSelectButton")
        self.gridLayout_3.addWidget(self.chatimgPathSelectButton, 5, 3, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 6, 1, 1, 3)
        self.label_15 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 5, 1, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_3.addWidget(self.label_17, 2, 1, 1, 1)
        self.needjavaDeserCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.needjavaDeserCheckBox.setEnabled(True)
        self.needjavaDeserCheckBox.setText("")
        self.needjavaDeserCheckBox.setChecked(True)
        self.needjavaDeserCheckBox.setTristate(False)
        self.needjavaDeserCheckBox.setObjectName("needjavaDeserCheckBox")
        self.gridLayout_3.addWidget(self.needjavaDeserCheckBox, 12, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_20.setObjectName("label_20")
        self.gridLayout_3.addWidget(self.label_20, 13, 1, 1, 3)
        self.label_13 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 7, 1, 1, 1)
        self.pttPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.pttPathInputBox.setEnabled(False)
        self.pttPathInputBox.setObjectName("pttPathInputBox")
        self.gridLayout_3.addWidget(self.pttPathInputBox, 7, 2, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_3.addWidget(self.label_16, 1, 1, 1, 1)
        self.selfQQInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.selfQQInputBox.setObjectName("selfQQInputBox")
        self.gridLayout_3.addWidget(self.selfQQInputBox, 0, 2, 1, 2)
        self.chatimgPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.chatimgPathInputBox.setEnabled(False)
        self.chatimgPathInputBox.setObjectName("chatimgPathInputBox")
        self.gridLayout_3.addWidget(self.chatimgPathInputBox, 5, 2, 1, 1)
        self.useVideoCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.useVideoCheckBox.setEnabled(True)
        self.useVideoCheckBox.setText("")
        self.useVideoCheckBox.setChecked(False)
        self.useVideoCheckBox.setTristate(False)
        self.useVideoCheckBox.setObjectName("useVideoCheckBox")
        self.gridLayout_3.addWidget(self.useVideoCheckBox, 9, 0, 1, 1)
        self.videoPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.videoPathSelectButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.videoPathSelectButton.setFont(font)
        self.videoPathSelectButton.setObjectName("videoPathSelectButton")
        self.gridLayout_3.addWidget(self.videoPathSelectButton, 9, 3, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 12, 1, 1, 3)
        self.videoPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.videoPathInputBox.setEnabled(False)
        self.videoPathInputBox.setObjectName("videoPathInputBox")
        self.gridLayout_3.addWidget(self.videoPathInputBox, 9, 2, 1, 1)
        self.modeSelectContainer = QtWidgets.QWidget(self.gridLayoutWidget_3)
        self.modeSelectContainer.setObjectName("modeSelectContainer")
        self.groupModeRadioButton = QtWidgets.QRadioButton(self.modeSelectContainer)
        self.groupModeRadioButton.setGeometry(QtCore.QRect(10, 0, 51, 16))
        self.groupModeRadioButton.setObjectName("groupModeRadioButton")
        self.friendModeRadioButton = QtWidgets.QRadioButton(self.modeSelectContainer)
        self.friendModeRadioButton.setGeometry(QtCore.QRect(90, 0, 75, 16))
        self.friendModeRadioButton.setChecked(True)
        self.friendModeRadioButton.setObjectName("friendModeRadioButton")
        self.gridLayout_3.addWidget(self.modeSelectContainer, 2, 2, 1, 2)
        self.usePttCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.usePttCheckBox.setEnabled(True)
        self.usePttCheckBox.setText("")
        self.usePttCheckBox.setChecked(False)
        self.usePttCheckBox.setTristate(False)
        self.usePttCheckBox.setObjectName("usePttCheckBox")
        self.gridLayout_3.addWidget(self.usePttCheckBox, 7, 0, 1, 1)
        self.checkBox_9 = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.checkBox_9.setEnabled(False)
        self.checkBox_9.setText("")
        self.checkBox_9.setChecked(True)
        self.checkBox_9.setTristate(False)
        self.checkBox_9.setObjectName("checkBox_9")
        self.gridLayout_3.addWidget(self.checkBox_9, 0, 0, 1, 1)
        self.checkBox_11 = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.checkBox_11.setEnabled(False)
        self.checkBox_11.setText("")
        self.checkBox_11.setChecked(True)
        self.checkBox_11.setTristate(False)
        self.checkBox_11.setObjectName("checkBox_11")
        self.gridLayout_3.addWidget(self.checkBox_11, 2, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 8, 1, 1, 3)
        self.label_11 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 11, 1, 1, 3)
        self.checkBox_10 = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.checkBox_10.setEnabled(False)
        self.checkBox_10.setText("")
        self.checkBox_10.setChecked(True)
        self.checkBox_10.setTristate(False)
        self.checkBox_10.setObjectName("checkBox_10")
        self.gridLayout_3.addWidget(self.checkBox_10, 1, 0, 1, 1)
        self.pttPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.pttPathSelectButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.pttPathSelectButton.setFont(font)
        self.pttPathSelectButton.setObjectName("pttPathSelectButton")
        self.gridLayout_3.addWidget(self.pttPathSelectButton, 7, 3, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_21.setObjectName("label_21")
        self.gridLayout_3.addWidget(self.label_21, 10, 1, 1, 3)
        self.findFilesModeContainer1 = QtWidgets.QWidget(self.parseConfigContainer)
        self.findFilesModeContainer1.setEnabled(True)
        self.findFilesModeContainer1.setGeometry(QtCore.QRect(10, 40, 371, 61))
        self.findFilesModeContainer1.setObjectName("findFilesModeContainer1")
        self.gridLayoutWidget = QtWidgets.QWidget(self.findFilesModeContainer1)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 371, 51))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.dataDirPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.dataDirPathSelectButton.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.dataDirPathSelectButton.setFont(font)
        self.dataDirPathSelectButton.setObjectName("dataDirPathSelectButton")
        self.gridLayout.addWidget(self.dataDirPathSelectButton, 0, 2, 1, 1)
        self.label_1 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_1.setFont(font)
        self.label_1.setObjectName("label_1")
        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)
        self.dataDirPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.dataDirPathInputBox.setEnabled(True)
        self.dataDirPathInputBox.setObjectName("dataDirPathInputBox")
        self.gridLayout.addWidget(self.dataDirPathInputBox, 0, 1, 1, 1)
        self.useSlowtableCheckBox2 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.useSlowtableCheckBox2.setChecked(True)
        self.useSlowtableCheckBox2.setTristate(False)
        self.useSlowtableCheckBox2.setObjectName("useSlowtableCheckBox2")
        self.gridLayout.addWidget(self.useSlowtableCheckBox2, 1, 0, 1, 2)
        self.findFilesModeContainer2 = QtWidgets.QWidget(self.parseConfigContainer)
        self.findFilesModeContainer2.setEnabled(False)
        self.findFilesModeContainer2.setGeometry(QtCore.QRect(10, 120, 371, 191))
        self.findFilesModeContainer2.setObjectName("findFilesModeContainer2")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.findFilesModeContainer2)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 371, 182))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 1, 1, 1)
        self.qqSlowtableDbPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.qqSlowtableDbPathSelectButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.qqSlowtableDbPathSelectButton.setFont(font)
        self.qqSlowtableDbPathSelectButton.setObjectName("qqSlowtableDbPathSelectButton")
        self.gridLayout_2.addWidget(self.qqSlowtableDbPathSelectButton, 2, 3, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 4, 1, 1, 3)
        self.useSlowtableCheckBox = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.useSlowtableCheckBox.setEnabled(False)
        self.useSlowtableCheckBox.setText("")
        self.useSlowtableCheckBox.setChecked(False)
        self.useSlowtableCheckBox.setTristate(False)
        self.useSlowtableCheckBox.setObjectName("useSlowtableCheckBox")
        self.gridLayout_2.addWidget(self.useSlowtableCheckBox, 2, 0, 1, 1)
        self.kcPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.kcPathSelectButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.kcPathSelectButton.setFont(font)
        self.kcPathSelectButton.setObjectName("kcPathSelectButton")
        self.gridLayout_2.addWidget(self.kcPathSelectButton, 6, 3, 1, 1)
        self.qqDbPathSelectButton = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.qqDbPathSelectButton.setFont(font)
        self.qqDbPathSelectButton.setObjectName("qqDbPathSelectButton")
        self.gridLayout_2.addWidget(self.qqDbPathSelectButton, 0, 3, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.checkBox.setEnabled(False)
        self.checkBox.setText("")
        self.checkBox.setChecked(True)
        self.checkBox.setTristate(False)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_2.addWidget(self.checkBox, 0, 0, 1, 1)
        self.kcPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.kcPathInputBox.setEnabled(False)
        self.kcPathInputBox.setObjectName("kcPathInputBox")
        self.gridLayout_2.addWidget(self.kcPathInputBox, 6, 2, 1, 1)
        self.qqDbPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.qqDbPathInputBox.setObjectName("qqDbPathInputBox")
        self.gridLayout_2.addWidget(self.qqDbPathInputBox, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 1, 1, 1)
        self.kcModeSelectContainer = QtWidgets.QWidget(self.gridLayoutWidget_2)
        self.kcModeSelectContainer.setObjectName("kcModeSelectContainer")
        self.kcInputModeRadioButton1 = QtWidgets.QRadioButton(self.kcModeSelectContainer)
        self.kcInputModeRadioButton1.setGeometry(QtCore.QRect(0, 0, 107, 16))
        self.kcInputModeRadioButton1.setMouseTracking(True)
        self.kcInputModeRadioButton1.setChecked(True)
        self.kcInputModeRadioButton1.setObjectName("kcInputModeRadioButton1")
        self.kcInputModeRadioButton2 = QtWidgets.QRadioButton(self.kcModeSelectContainer)
        self.kcInputModeRadioButton2.setGeometry(QtCore.QRect(0, 30, 101, 16))
        self.kcInputModeRadioButton2.setMouseTracking(True)
        self.kcInputModeRadioButton2.setObjectName("kcInputModeRadioButton2")
        self.gridLayout_2.addWidget(self.kcModeSelectContainer, 5, 1, 2, 1)
        self.qqSlowtableDbPathInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.qqSlowtableDbPathInputBox.setEnabled(False)
        self.qqSlowtableDbPathInputBox.setObjectName("qqSlowtableDbPathInputBox")
        self.gridLayout_2.addWidget(self.qqSlowtableDbPathInputBox, 2, 2, 1, 1)
        self.checkBox_4 = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.checkBox_4.setEnabled(False)
        self.checkBox_4.setText("")
        self.checkBox_4.setChecked(True)
        self.checkBox_4.setTristate(False)
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout_2.addWidget(self.checkBox_4, 4, 0, 1, 1)
        self.kcInputBox = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.kcInputBox.setObjectName("kcInputBox")
        self.gridLayout_2.addWidget(self.kcInputBox, 5, 2, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 1, 1, 3)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 1, 1, 3)
        self.logBox = QtWidgets.QTextBrowser(self.centralwidget)
        self.logBox.setGeometry(QtCore.QRect(400, 10, 281, 591))
        self.logBox.setObjectName("logBox")
        self.starButton = QtWidgets.QPushButton(self.centralwidget)
        self.starButton.setGeometry(QtCore.QRect(570, 650, 121, 41))
        self.starButton.setStyleSheet("QPushButton {\n"
"    border-image: url(:/Image/star.jpg)\n"
"}")
        self.starButton.setText("")
        self.starButton.setObjectName("starButton")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(260, 670, 181, 21))
        self.label_6.setObjectName("label_6")
        self.startParseButton = QtWidgets.QPushButton(self.centralwidget)
        self.startParseButton.setGeometry(QtCore.QRect(0, 630, 241, 61))
        self.startParseButton.setObjectName("startParseButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 693, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "QQHistoryExport-QQ聊天记录导出"))
        self.parseConfigContainer.setTitle(_translate("MainWindow", "解析设置"))
        self.findFilesModeRadioButton1.setText(_translate("MainWindow", "选择整个Data文件夹"))
        self.findFilesModeRadioButton2.setText(_translate("MainWindow", "分别选取每个文件"))
        self.label_8.setText(_translate("MainWindow", "解析选项"))
        self.label_18.setText(_translate("MainWindow", "QQ表情"))
        self.label_19.setText(_translate("MainWindow", "shortvideo文件夹"))
        self.qqEmojiVerRadioButton1.setText(_translate("MainWindow", "旧版"))
        self.qqEmojiVerRadioButton2.setText(_translate("MainWindow", "新版"))
        self.chatimgPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.label_10.setText(_translate("MainWindow", "聊天图片"))
        self.label_15.setText(_translate("MainWindow", "你自己的QQ号"))
        self.label_12.setText(_translate("MainWindow", "chatimg文件夹"))
        self.label_17.setText(_translate("MainWindow", "模式"))
        self.label_20.setText(_translate("MainWindow", "包括：引用消息的引用部分，群文件信息"))
        self.label_13.setText(_translate("MainWindow", "ptt文件夹"))
        self.label_16.setText(_translate("MainWindow", "目标QQ号"))
        self.videoPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.label_14.setText(_translate("MainWindow", "java序列化解析，需要安装java环境"))
        self.groupModeRadioButton.setText(_translate("MainWindow", "群聊"))
        self.friendModeRadioButton.setText(_translate("MainWindow", "私聊"))
        self.label_9.setText(_translate("MainWindow", "语音文件"))
        self.label_11.setText(_translate("MainWindow", "大表情 即单独发QQ表情出来的大表情"))
        self.pttPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.label_21.setText(_translate("MainWindow", "视频文件"))
        self.dataDirPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.label_1.setText(_translate("MainWindow", "com.tencent.mobileqq文件夹"))
        self.useSlowtableCheckBox2.setText(_translate("MainWindow", "解析两个月以前的聊天记录"))
        self.label_3.setText(_translate("MainWindow", "QQ号_slowtable.db"))
        self.qqSlowtableDbPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.label_7.setText(_translate("MainWindow", "解密秘钥（必填，就是你手机的IMEI）"))
        self.kcPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.qqDbPathSelectButton.setText(_translate("MainWindow", "选取"))
        self.label_2.setText(_translate("MainWindow", "QQ号.db"))
        self.kcInputModeRadioButton1.setText(_translate("MainWindow", "手动输入IMEI"))
        self.kcInputModeRadioButton2.setText(_translate("MainWindow", "选取kc文件路径"))
        self.label_5.setText(_translate("MainWindow", "两个月以内的聊天记录"))
        self.label_4.setText(_translate("MainWindow", "两个月以前的聊天记录"))
        self.label_6.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:14pt;\">by xxxx  v1.0.0</span></p></body></html>"))
        self.startParseButton.setText(_translate("MainWindow", "开始解析"))
        self.menu.setTitle(_translate("MainWindow", "解析"))
        self.menu_2.setTitle(_translate("MainWindow", "生成"))
import src.GUI.res_rc
