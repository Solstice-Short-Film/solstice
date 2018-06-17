#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shader_utils.py
# by Tomas Poveda
# Module that contains utility functions related with shaders
# ______________________________________________________________________
# ==================================================================="""

import os

from maya import cmds, OpenMayaUI

from Qt.QtWidgets import *
from Qt.QtGui import *
try:
    from shiboken import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance


def get_shader_swatch(shader_name, render_size=100, swatch_width=100, swatch_height=100):
    """
    Returns a Shader watch as QWidget
    :param shader_name: str
    :param render_size: int
    :param swatch_width: int
    :param swatch_height: int
    :return: QWidget
    """

    tempwin = cmds.window()
    cmds.columnLayout()
    swatch_port = cmds.swatchDisplayPort(renderSize=render_size, widthHeight=(swatch_width, swatch_height), shadingNode=shader_name)
    if not swatch_port:
        return None

    swatch_ptr = OpenMayaUI.MQtUtil.findControl(swatch_port)
    swatch = wrapInstance(long(swatch_ptr), QWidget)
    # cmds.deleteUI(tempwin)

    return swatch


def export_shader_swatch_as_image(shader_name, export_path=None, render_size=100, swatch_width=100, swatch_height=100, format='png', get_pixmap=False):
    """
    Export shader swatch as image
    :param shader_name: str
    :param export_path: str
    :param render_size: int
    :param swatch_width: int
    :param swatch_height: int
    :param format: str
    :return: variant, None || str
    """

    swatch = get_shader_swatch(shader_name=shader_name, render_size=render_size, swatch_width=swatch_width, swatch_height=swatch_height)
    swatch_pixmap = QPixmap(swatch.size())
    swatch.render(swatch_pixmap)
    export_path = os.path.join(export_path, shader_name+'.'+format)
    swatch_pixmap.save(export_path)

    if get_pixmap:
        # swatch.deleteLater()
        # swatch = None
        return swatch_pixmap


    if export_path is None:
        return None
    if not os.path.exists(export_path):
        return None
    export_path = os.path.join(export_path, shader_name+'.'+format)
    swatch_pixmap.save(export_path)
    # swatch.deleteLater()
    # swatch = None

    return export_path