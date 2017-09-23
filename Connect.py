# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Connect.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Connect(object):
    def setupUi(self, Connect):
        Connect.setObjectName("Connect")
        Connect.resize(424, 319)
        self.listConnect = QtWidgets.QListWidget(Connect)
        self.listConnect.setGeometry(QtCore.QRect(40, 30, 341, 181))
        self.listConnect.setViewMode(QtWidgets.QListView.ListMode)
        self.listConnect.setObjectName("listConnect")
        self.AddConnect = QtWidgets.QPushButton(Connect)
        self.AddConnect.setGeometry(QtCore.QRect(320, 270, 61, 23))
        self.AddConnect.setObjectName("AddConnect")
        self.Select = QtWidgets.QPushButton(Connect)
        self.Select.setGeometry(QtCore.QRect(320, 240, 61, 23))
        self.Select.setObjectName("Select")
        self.label = QtWidgets.QLabel(Connect)
        self.label.setGeometry(QtCore.QRect(40, 10, 54, 12))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Connect)
        self.label_2.setGeometry(QtCore.QRect(40, 230, 61, 16))
        self.label_2.setObjectName("label_2")
        self.connectChoice = QtWidgets.QPlainTextEdit(Connect)
        self.connectChoice.setGeometry(QtCore.QRect(40, 250, 271, 40))
        self.connectChoice.setObjectName("connectChoice")

        self.Select.clicked.connect(self.choice)
        self.AddConnect.clicked.connect(self.decide)

        self.retranslateUi(Connect)
        QtCore.QMetaObject.connectSlotsByName(Connect)

    def retranslateUi(self, Connect):
        _translate = QtCore.QCoreApplication.translate
        Connect.setWindowTitle(_translate("Connect", "最近联系人"))
        self.AddConnect.setText(_translate("Connect", "Add"))
        self.Select.setText(_translate("Connect", "Select"))
        self.label.setText(_translate("Connect", "用户列表"))
        self.label_2.setText(_translate("Connect", "添加收信人"))

