# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\ASUS\programming\qt_programs\wordsearch\solver.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(828, 802)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_2 = QtWidgets.QFrame(self.frame_3)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.grid_input = QtWidgets.QTextEdit(self.frame_2)
        self.grid_input.setObjectName("grid_input")
        self.verticalLayout.addWidget(self.grid_input)
        self.frame_4 = QtWidgets.QFrame(self.frame_2)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.formLayout = QtWidgets.QFormLayout(self.frame_4)
        self.formLayout.setContentsMargins(0, -1, -1, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtWidgets.QLabel(self.frame_4)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.rows_input = QtWidgets.QSpinBox(self.frame_4)
        self.rows_input.setMinimum(3)
        self.rows_input.setObjectName("rows_input")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.rows_input)
        self.verticalLayout.addWidget(self.frame_4)
        self.frame_5 = QtWidgets.QFrame(self.frame_2)
        self.frame_5.setMaximumSize(QtCore.QSize(16777215, 100))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.split_rows_button = QtWidgets.QPushButton(self.frame_5)
        self.split_rows_button.setObjectName("split_rows_button")
        self.horizontalLayout_2.addWidget(self.split_rows_button)
        self.verticalLayout.addWidget(self.frame_5)
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setMinimumSize(QtCore.QSize(0, 0))
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.load_grid_button = QtWidgets.QPushButton(self.frame_2)
        self.load_grid_button.setObjectName("load_grid_button")
        self.verticalLayout.addWidget(self.load_grid_button)
        self.horizontalLayout.addWidget(self.frame_2)
        self.frame = QtWidgets.QFrame(self.frame_3)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.words_input = QtWidgets.QTextEdit(self.frame)
        self.words_input.setObjectName("words_input")
        self.verticalLayout_2.addWidget(self.words_input)
        self.split_button = QtWidgets.QPushButton(self.frame)
        self.split_button.setObjectName("split_button")
        self.verticalLayout_2.addWidget(self.split_button)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.load_words_solver = QtWidgets.QPushButton(self.frame)
        self.load_words_solver.setObjectName("load_words_solver")
        self.verticalLayout_2.addWidget(self.load_words_solver)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 2)
        self.verticalLayout_3.addWidget(self.frame_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(Form)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Wordsearch solver"))
        self.label.setText(_translate("Form", "Paste Wordsearch Grid"))
        self.label_4.setText(_translate("Form", "Rows"))
        self.split_rows_button.setText(_translate("Form", "Split by rows"))
        self.label_5.setText(_translate("Form", "Other options"))
        self.load_grid_button.setText(_translate("Form", "Load From File"))
        self.label_2.setText(_translate("Form", "Paste words"))
        self.split_button.setText(_translate("Form", "Split words"))
        self.label_3.setText(_translate("Form", "Word Options"))
        self.load_words_solver.setText(_translate("Form", "Load Words"))
