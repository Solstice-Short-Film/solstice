#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shader_utils.py
# by Tomas Poveda
# Module that contains utility functions related with files
# ______________________________________________________________________
# ==================================================================="""

import maya.cmds as cmds


def get_file_paths():
    """
    Returns all file paths in current Maya scene
    :return: list<str>
    """

    file_paths = list()
    files = cmds.ls(type='file')
    for f in files:
        f_path = cmds.getAttr(f + '.fileTextureName')
        file_paths.append(f_path)

    return file_paths


def print_file_paths():
    """
    This function prints all file paths
    """

    files = cmds.ls(type='file')
    for f in files:
        f_path = cmds.getAttr(f + '.fileTextureName')
        print(f_path)


def clean_file_paths():
    """
    Function that updates current scene file paths
    """

    files = cmds.ls(type='file')
    for f in files:
        f_path = cmds.getAttr(f + '.fileTextureName')
        clean_path = f_path.replace('\\', '/')
        cmds.setAttr("{0}.fileTextureName".format(f), lock=False)
        cmds.setAttr("{0}.fileTextureName".format(f), clean_path, type="string")
