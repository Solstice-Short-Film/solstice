#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetbuilder.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
# ______________________________________________________________________
# ==================================================================="""

import os
import json

from solstice_gui import solstice_windows

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice_pipeline as sp
from solstice_gui import solstice_splitters
from solstice_utils import solstice_image as img


class AssetBuilder(solstice_windows.Window, object):

    name = 'Asset Builder'
    title = 'Solstice Tools - Asset Builder'
    version = '1.0'
    docked = False

    def __init__(self, name='AssetBuilderWindow', parent=None, **kwargs):
        super(AssetBuilder, self).__init__(name=name, parent=parent, **kwargs)

        self.set_logo('solstice_assetbuilder_logo')

        self._current_icon_path = None
        self._current_preview_path = None

        self._icon_btn = QPushButton('Icon')
        self._icon_btn.setMinimumSize(QSize(150, 150))
        self._icon_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._preview_btn = QPushButton('Preview')
        self._preview_btn.setMinimumSize(QSize(150, 150))
        self._preview_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._description_text = QTextEdit()
        self._description_text.setPlaceholderText('Description')

        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(5, 10, 5, 5)
        self.main_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        icon_layout.addWidget(self._icon_btn, Qt.AlignCenter)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(5, 5, 5, 10)
        self.main_layout.addLayout(preview_layout)
        preview_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        preview_layout.addWidget(self._preview_btn, Qt.AlignCenter)
        preview_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(self._description_text)

        self.main_layout.addItem(QSpacerItem(0, 5))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        save_btn = QPushButton('Generate Asset File')
        load_btn = QPushButton('Load Asset File')
        self.main_layout.addItem(QSpacerItem(0, 10))
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(load_btn)
        self.main_layout.addLayout(buttons_layout)

        # ============================================================================

        self._icon_btn.clicked.connect(self._set_icon)
        self._preview_btn.clicked.connect(self._set_preview)
        save_btn.clicked.connect(self._save_asset)
        load_btn.clicked.connect(self._load_asset)

    def _save_asset(self):
        out_dict = dict()
        out_dict['asset'] = dict()
        if self._current_icon_path and os.path.isfile(self._current_icon_path):
            image_format = os.path.splitext(self._current_icon_path)[1][1:].upper()
            icon_out = img.image_to_base64(image_path=self._current_icon_path, image_format=image_format)
            out_dict['asset']['icon'] = icon_out
            out_dict['asset']['icon_format'] = image_format
        out_dict['asset']['preview'] = ''
        out_dict['asset']['preview_format'] = ''
        out_dict['asset']['description'] = self._description_text.toPlainText()

        save_file = QFileDialog.getSaveFileName(self, 'Set folder to store asset data', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        if os.path.exists(os.path.dirname(save_file)):
            with open(save_file, 'w') as f:
                json.dump(out_dict, f)

            # try:
            #     import subprocess
            #     subprocess.Popen(r'explorer /select,"{0}"'.format(save_file))
            # except Exception:
            #     pass

    def _load_asset(self):
        load_file = QFileDialog.getOpenFileName(self, 'Select asset data file to open', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        if os.path.isfile(load_file):
            data = None
            with open(load_file, 'r') as f:
                data = json.load(f)
            if data:
                asset_icon = data['asset']['icon']
                icon_format = data['asset']['icon_format']
                asset_preview = data['asset']['preview']
                preview_format = data['asset']['preview_format']

                if asset_icon is not None and asset_icon != '':
                    asset_icon = asset_icon.encode('utf-8')
                    self._icon_btn.setIcon(QPixmap.fromImage(img.base64_to_image(asset_icon)))
                    self._icon_btn.setText('')
                if asset_preview is not None and asset_preview != '':
                    asset_preview = asset_preview.encode('utf-8')
                    self._preview_btn.setIcon(img.base64_to_icon(asset_preview, icon_format='PNG'))
                    self._preview_btn.setText('')
                self._description_text.setText(data['asset']['description'])

    def _set_icon(self):
        file_dialog = QFileDialog(self)
        icon_file_path = file_dialog.getOpenFileName(self, 'Select Icon File', sp.get_solstice_assets_path(), 'PNG Files (*.png);; JPG Files (*.jpg)')
        if icon_file_path and os.path.isfile(icon_file_path[0]):
            self._icon_btn.setIcon(QIcon(QPixmap(icon_file_path[0])))
            self._icon_btn.setText('')
            self._current_icon_path = icon_file_path[0]

    def _set_preview(self):
        pass


def run():
    reload(solstice_splitters)
    reload(img)
    AssetBuilder().run()

