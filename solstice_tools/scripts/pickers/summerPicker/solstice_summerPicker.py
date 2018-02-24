#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_summerPicker.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Customized picker for Summer Character
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


# Import standard Python modules
from functools import partial
import os

# Import custom modules
from solstice_tools.scripts.pickers.picker import solstice_pickerWindow as window
from solstice_tools.scripts.pickers.picker import solstice_pickerUtils as utils
import solstice_summerBodyPicker as  bodyPicker
import solstice_summerFacialPicker as facialPicker

# --------------------------------------------------------------------------------------------
imagesPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
dataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
# --------------------------------------------------------------------------------------------


class Solstice_SummerPicker(window.Solstice_PickerWindow, object):

    def __init__(self, pickerName, pickerTitle, charName, parent=None, fullWindow=False):

        self._fullWindow = fullWindow
        self._bodyPickerData = os.path.join(dataPath, 'summerBodyPickerData.json')
        self._facialPickerData = os.path.join(dataPath, 'summerFacialPickerData.json')

        super(Solstice_SummerPicker, self).__init__(pickerName=pickerName, pickerTitle=pickerTitle, charName=charName, parent=parent)

    def initSetup(self):

        super(Solstice_SummerPicker, self).initSetup()

        return True

    def bodyPickerData(self):
        return self._bodyPickerData

    def facialPickerData(self):
        return self._facialPickerData

    def toolUI(self):

        # Init and check tool
        if self.initSetup() == True:

            # Init default UI for all pickers
            super(Solstice_SummerPicker, self).toolUI()

            self.setCharacterImage(os.path.join(imagesPath, 'summer_icon.png'))
            #
            self.bp = bodyPicker.solstice_summerBodyPicker(dataPath=self.bodyPickerData(), imagePath=os.path.join(imagesPath, 'pickerSummer_body.svg'))
            self.fp = facialPicker.solstice_summerFacialPicker(dataPath=self.facialPickerData(), imagePath=os.path.join(imagesPath, 'pickerSummer_facial.svg'))

            if self._fullWindow:
                self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                fullPickersLayout = QHBoxLayout()
                fullPickersLayout.setContentsMargins(5,5,5,5)
                fullPickersLayout.setSpacing(2)
                self.mainLayout.addLayout(fullPickersLayout)
                for picker in [self.bp, self.fp]:
                    fullPickersLayout.addWidget(picker)

            else:
                self.charTab = QTabWidget()
                self.mainLayout.addWidget(self.charTab)
                self.charTab.addTab(self.bp, 'Body')
                self.charTab.addTab(self.fp, 'Facial')

            self.updatePickers()

    def updatePickers(self):
        pass
        # for picker in [self.bp, self.fp]:
        #     picker.setNamespace(self.namespace.currentText())

    def setFullWindow(self, fullWindow):
        self._fullWindow = fullWindow

    def reloadData(self):
        self.bp.reloadData()


def initPicker(fullWindow=True):
    utils.dock_window(pickerName='summerPicker', pickerTitle='Solstice - Summer Picker', charName='Summer', dialog_class=Solstice_SummerPicker)
