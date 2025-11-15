import importlib
import importlib.util
import os

from pathlib import Path


def get_python_files(src='step_definitions'):
    folder_path = Path(src)
    py_files = [str(file) for file in folder_path.glob("**/*.py")]
    return py_files


def import_module_from_file(module_name_to_import, py_path):
    module_spec = importlib.util.spec_from_file_location(module_name_to_import, py_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module, )
    return module


def import_all_modules_in_folder(src, star_import=False):
    my_py_files = get_python_files(src)
    for py_file in my_py_files:
        module_name = Path(py_file).stem  # os.path.split(py_file)[-1].strip(".py")
        imported_module = import_module_from_file(module_name, py_file)
        if star_import:
            for obj in dir(imported_module):
                globals()[obj] = imported_module.__dict__[obj]
        else:
            globals()[module_name] = imported_module
    return


def import_all_modules_in_package(package_name):
    """
    Uses Importlib to cheeck to load all modules in package and send the list of imported modules.
    If there are sub packages, it will recursively load them too.
    :param package_name:
    :return:
    """
    # step_def_spec = importlib.util.find_spec(package_name)
    #
    imported_modules = []
    #
    # if step_def_spec is None or step_def_spec.submodule_search_locations is None:
    #     logger.error(
    #         "Could not find spec in search location for package: {}, step_def_spec={}, cwd={}".format(package_name,
    #                                                                                                   step_def_spec,
    #                                                                                                   os.getcwd()))
    #     return imported_modules

    # for search_location in step_def_spec.submodule_search_locations:

    search_location = Path(os.getcwd(), *package_name.split("."))
    # For all python files in the package folder
    my_py_files = [str(file) for file in Path(search_location).glob("*.py") if file.name != "__init__.py"]

    for module_name in my_py_files:
        module_name = Path(module_name).stem  # os.path.split(module_name)[-1].strip(".py")
        imported_module = importlib.import_module(f"{package_name}.{module_name}")
        imported_modules.append(imported_module)

    # For all sub folders in the package folder
    my_sub_folders = [str(folder) for folder in Path(search_location).glob("*/") if
                      (folder / "__init__.py").exists()]
    for module_name in my_sub_folders:
        module_name = Path(module_name).name  # os.path.split(module_name)[-1]
        sub_imported_modules = import_all_modules_in_package(
            f"{package_name}.{module_name}")
        imported_modules.extend(sub_imported_modules)

    return imported_modules
