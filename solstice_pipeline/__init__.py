#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Initiailzer class for solstice_pipeline
# ==================================================================="""

import os
import re
import sys
import json
import pkgutil
import datetime
import importlib
from types import ModuleType
from collections import OrderedDict
if sys.version_info[:2] > (2, 7):
    from importlib import reload
else:
    from imp import reload

import maya.cmds as cmds
import maya.mel as mel
import maya.utils

import solstice_pipeline

root_path = os.path.dirname(os.path.abspath(__file__))
loaded_modules = OrderedDict()
reload_modules = list()
logger = None
info_dialog = None
settings = None

# =================================================================================

solstice_project_id = '2/2252d6c8-407d-4419-a186-cf90760c9967/'
solstice_project_id_raw = '2252d6c8-407d-4419-a186-cf90760c9967'
solstice_project_id_full = '_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'
valid_categories = ['textures', 'model', 'shading', 'groom']            # NOTE: The order is important, textures MUST go first

# =================================================================================


def update_paths():
    extra_paths = [os.path.join(root_path, 'externals'), os.path.join(root_path, 'icons')]
    for path in extra_paths:
        if os.path.exists(path) and path not in sys.path:
                sys.path.append(path)

    for subdir, dirs, files in os.walk(root_path):
        if subdir not in sys.path:
            sys.path.append(subdir)


def import_module(package_name):
    try:
        mod = importlib.import_module(package_name)
        solstice_pipeline.logger.debug('Imported: {}'.format(package_name))
        if mod and isinstance(mod, ModuleType):
            return mod
        return None
    except (ImportError, AttributeError) as e:
        solstice_pipeline.logger.debug('FAILED IMPORT: {} -> {}'.format(package_name, str(e)))
        pass


def import_modules(module_name, only_packages=False, order=[]):
    names, paths = explore_package(module_name=module_name, only_packages=only_packages)
    ordered_names = list()
    ordered_paths = list()
    temp_index = 0
    i = -1
    for o in order:
        for n, p in zip(names, paths):
            if str(n) == str(o):
                i += 1
                temp_index = i
                ordered_names.append(n)
                ordered_paths.append(p)
            elif n.endswith(o):
                ordered_names.insert(temp_index+1, n)
                ordered_paths.insert(temp_index+1, n)
                temp_index += 1
            elif str(o) in str(n):
                ordered_names.append(n)
                ordered_paths.append(p)

    ordered_names.extend(names)
    ordered_paths.extend(paths)

    names_set = set()
    paths_set = set()
    module_names = [x for x in ordered_names if not (x in names_set or names_set.add(x))]
    module_paths = [x for x in ordered_paths if not (x in paths_set or paths_set.add(x))]

    reloaded_names = list()
    reloaded_paths = list()
    for n, p in zip(names, paths):
        reloaded_names.append(n)
        reloaded_paths.append(p)

    for name, _ in zip(module_names, module_paths):
        if name not in loaded_modules.keys():
            mod = import_module(name)
            if mod:
                if isinstance(mod, ModuleType):
                    loaded_modules[mod.__name__] = [os.path.dirname(mod.__file__), mod]
                    reload_modules.append(mod)

    for name, path in zip(module_names, module_paths):
        order = list()
        if name in loaded_modules.keys():
            mod = loaded_modules[name][1]
            if hasattr(mod, 'order'):
                order = mod.order
        import_modules(module_name=path, only_packages=False, order=order)


def reload_all():
    """
    Loops through all solstice_tools modules and reload them ane by one
    Used to increase iteration times
    """

    for mod in reload_modules:
        try:
            solstice_pipeline.logger.debug('Reloading module {0} ...'.format(mod))
            reload(mod)
        except Exception as e:
            solstice_pipeline.logger.debug('Impossible to import {0} module : {1}'.format(mod, str(e)))


def explore_package(module_name, only_packages=False):
    """
    Load module iteratively
    :param module_name: str, name of the module
    :return: list<str>, list<str>, list of loaded module names and list of loaded module paths
    """

    module_names = list()
    module_paths = list()

    def foo(name, only_packages):
        for importer, m_name, is_pkg in pkgutil.iter_modules([name]):
            mod_path = name + "//" + m_name
            mod_name = 'solstice_pipeline.' + os.path.relpath(mod_path, solstice_pipeline.__path__[0]).replace('\\', '.')
            if only_packages:
                if is_pkg:
                    module_paths.append(mod_path)
                    module_names.append(mod_name)
            else:
                module_paths.append(mod_path)
                module_names.append(mod_name)
    foo(module_name, only_packages)

    return module_names, module_paths


def create_solstice_logger():
    """
    Creates and initializes solstice logger
    """

    from solstice_utils import solstice_logger
    global logger
    logger = solstice_logger.Logger(name='solstice', level=solstice_logger.LoggerLevel.DEBUG)
    logger.debug('Initializing Solstice Tools ...')


def create_solstice_settings():
    """
    Creates a settings file that can be accessed globally by all tools
    """

    from solstice_utils import solstice_config
    global settings
    settings = solstice_config.create_config('solstice_pipeline')


def create_solstice_info_window():
    """
    Creates a global window that is used to show different type of info
    """

    from solstice_gui import solstice_info_dialog
    global info_dialog
    info_dialog = solstice_info_dialog.InfoDialog()


def create_solstice_shelf():
    """
    Creates Solstice Tools shelf
    """

    solstice_pipeline.logger.debug('Building Solstice Tools Shelf ...')

    from solstice_gui import solstice_shelf

    try:
        s_shelf = solstice_shelf.SolsticeShelf()
        s_shelf.create(delete_if_exists=True)
        shelf_file = get_solstice_shelf_file()
        if shelf_file and os.path.isfile(shelf_file):
            s_shelf.build(shelf_file=shelf_file)
            s_shelf.set_as_active()
    except Exception as e:
        solstice_pipeline.logger.warning('Error during Solstice Shelf Creation: {}'.format(e))


def create_solstice_menu():
    """
    Create Solstice Tools menu
    """

    solstice_pipeline.logger.debug('Building Solstice Tools Menu ...')

    from solstice_gui import solstice_menu
    from solstice_utils import solstice_maya_utils

    try:
        solstice_maya_utils.remove_menu('Solstice')
    except Exception:
        pass

    try:
        s_menu = solstice_menu.SolsticeMenu()
        menu_file = get_solstice_menu_file()
        if menu_file and os.path.isfile(menu_file):
            s_menu.create_menu(file_path=menu_file, parent_menu='Solstice')
    except Exception as e:
        solstice_pipeline.logger.warning('Error during Solstice Menu Creation: {}'.format(e))


def update_solstice_project():
    """
    Set the current Maya project to the path where Solstice is located inside Artella folder
    """

    try:
        solstice_pipeline.logger.debug('Setting Solstice Project ...')
        solstice_project_folder = os.environ.get('SOLSTICE_PROJECT', 'folder-not-defined')
        if solstice_project_folder and os.path.exists(solstice_project_folder):
            cmds.workspace(solstice_project_folder, openWorkspace=True)
            solstice_pipeline.logger.debug('Solstice Project setup successfully! => {}'.format(solstice_project_folder))
        else:
            solstice_pipeline.logger.debug('Unable to set Solstice Project! => {}'.format(solstice_project_folder))
    except Exception as e:
        solstice_pipeline.logger.debug(str(e))


def update_solstice_project_path():
    """
    Updates environment variable that stores Solstice Project path and returns
    the stored path
    :return: str
    """

    artella_var = os.environ.get('ART_LOCAL_ROOT', None)
    if artella_var and os.path.exists(artella_var):
        os.environ['SOLSTICE_PROJECT'] = '{0}/_art/production/{1}'.format(artella_var, solstice_project_id)
    else:
        logger.debug('ERROR: Impossible to set Solstice Project Environment Variable! Contact TD please!')


def get_solstice_project_path():
    """
    Returns Solstice Project path
    :return: str
    """
    env_var = os.environ.get('SOLSTICE_PROJECT', None)
    if env_var is None:
        update_solstice_project_path()

    env_var = os.environ.get('SOLSTICE_PROJECT', None)
    if env_var is None:
        raise RuntimeError('Solstice Project not setted up properly. Is Artella running? Contact TD!')

    return os.environ.get('SOLSTICE_PROJECT')


def get_solstice_shelf_file():
    """
    Returns Solstice Shelf File
    :return: str
    """

    shelf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shelf.xml')
    if not os.path.exists(shelf_file):
        solstice_pipeline.logger.warning('Shelf file: {} does not exists!'.format(shelf_file))
        return False

    return shelf_file


def get_solstice_menu_file():
    """
    Returns Solstice Menu File
    :return: str
    """

    menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu.json')
    if not os.path.exists(menu_file):
        solstice_pipeline.logger.warning('Menu file: {} does not exists!'.format(menu_file))
        return False

    return menu_file


def get_solstice_assets_path():
    """
    Returns Solstice Project Assets path
    :return: str
    """

    assets_path = os.path.join(get_solstice_project_path(), 'Assets')
    if os.path.exists(assets_path):
        # sp.logger.debug('Getting Assets Path: {0}'.format(assets_path))
        return assets_path
    else:
        logger.debug('Asset Path does not exists!: {0}'.format(assets_path))
        return None


def get_solstice_production_path():
    """
    Returns Solstice Project Production path
    :return: str
    """

    production_path = os.path.join(get_solstice_project_path(), 'Production')
    if os.path.exists(production_path):
        return production_path
    else:
        logger.debug('Production Path does not exists!: {0}'.format(production_path))
        return None


def get_asset_version(name):
    """
    Returns the version of a specific given asset (model_v001, return [v001, 001, 1])
    :param name: str
    :return: list<str, int>
    """

    string_version = name[-4:]
    int_version = map(int, re.findall('\d+', string_version))[0]
    int_version_formatted = '{0:03}'.format(int_version)

    return [string_version, int_version, int_version_formatted]


def register_asset(asset_name):
    """
    Adds the given asset to the local registry of assets
    This register is used to check last time a user synchronized a specific asset
    :param asset_name: str, name of the asset to register
    :return: str, sync time
    """

    invalid_names = ['__working__']
    if asset_name in invalid_names:
        return

    now = datetime.datetime.now()
    sync_time = now.strftime("%m/%d/%Y %H:%M:%S")
    logger.debug('Registering Asset Sync: {0} - {1}'.format(asset_name, sync_time))
    settings.set(settings.app_name, asset_name, str(sync_time))
    settings.update()
    return sync_time


def init_solstice_environment_variables():
    """
    Initializes all necessary environment variables used in Solstice Tools
    """

    def handleMessage(jsonMsg):
        try:
            msg = json.loads(jsonMsg)

            if type(msg) == dict:
                command_name = msg['CommandName']
                args = msg['CommandArgs']

                if command_name == 'open':
                    maya_file = args['path']
                    opened_file = cmds.file(maya_file, open=True, force=True)
                    scenefile_type = cmds.file(q=True, type=True)
                    if type(scenefile_type) == list:
                        scenefile_type = scenefile_type[0]
                    filepath = maya_file.replace('\\', '/')
                    mel.eval('$filepath = "{filepath}";'.format(filepath=filepath))
                    mel.eval('addRecentFile $filepath "{scenefile_type}";'.format(scenefile_type=scenefile_type))
                elif command_name == 'import':
                    path = args['path']
                    cmds.file(path, i=True, preserveReferences=True)
                elif command_name == 'reference':
                    path = args['path']
                    use_rename = cmds.optionVar(q='referenceOptionsUseRenamePrefix')
                    if use_rename:
                        namespace = cmds.optionVar(q='referenceOptionsRenamePrefix')
                        cmds.file(path, reference=True, namespace=namespace)
                    else:
                        filename = os.path.basename(path)
                        namespace, _ = os.path.splitext(filename)
                        cmds.file(path, reference=True, namespace=namespace)
                else:
                    solstice_pipeline.logger.debug("Unknown command: %s", command_name)

        except Exception, e:
            solstice_pipeline.logger.debug.warn("Error: %s", e)

    def passMsgToMainThread(jsonMsg):
        maya.utils.executeInMainThreadWithResult(handleMessage, jsonMsg)

    from solstice_tools import solstice_changelog
    from solstice_utils import solstice_artella_utils

    solstice_pipeline.logger.debug('Initializing environment variables for Solstice Tools ...')
    solstice_artella_utils.update_local_artella_root()

    artella_var = os.environ.get('ART_LOCAL_ROOT')
    solstice_pipeline.logger.debug('Artella environment variable is set to: {}'.format(artella_var))
    if artella_var and os.path.exists(artella_var):
        os.environ['SOLSTICE_PROJECT'] = '{}/_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'.format(artella_var)
    else:
        solstice_pipeline.logger.debug('Impossible to set Artella environment variables! Solstice Tools wont work correctly! Please contact TD!')

    solstice_pipeline.logger.debug('=' * 100)
    solstice_pipeline.logger.debug("Solstices Tools initialization completed!")
    solstice_pipeline.logger.debug('=' * 100)
    solstice_pipeline.logger.debug('*' * 100)
    solstice_pipeline.logger.debug('-' * 100)
    solstice_pipeline.logger.debug('\n')

    if os.environ.get('SOLSTICE_PIPELINE_SHOW'):
        solstice_changelog.run()

def init():
    # update_paths()
    create_solstice_logger()
    import_modules(solstice_pipeline.__path__[0], only_packages=True, order=['solstice_pipeline.solstice_utils', 'solstice_pipeline.solstice_gui', 'solstice_pipeline.solstice_tools'])
    reload_all()
    create_solstice_settings()
    create_solstice_info_window()
    create_solstice_shelf()
    create_solstice_menu()
    init_solstice_environment_variables()
    update_solstice_project()



