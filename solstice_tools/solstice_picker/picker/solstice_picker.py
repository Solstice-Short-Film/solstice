#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: sPicker.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Customized picker for Solstice characters
______________________________________________________________________
==================================================================="""

# Import PySide modules
try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import os

import solstice_pickerView

class solstice_picker(QWidget, object):
    def __init__(self, imagePath=None, parent=None):
        super(solstice_picker, self).__init__(parent=parent)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

        checkedImagePath = None
        if os.path.isfile(imagePath):
            checkedImagePath = imagePath

        self.view = solstice_pickerView.solstice_pickerView(imagePath=checkedImagePath)
        self.mainLayout.addWidget(self.view)

    def setView(self, view):
        if not view:
            return
        if self.view:
            self.view.setParent(None)
            self.view.deleteLater()
        self.view = view
        self.addWidget(self.view)

    def view(self):
        return self.view

    def addButton(self):
        self.view.scene().addButton()