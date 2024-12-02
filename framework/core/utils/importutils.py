import importlib
import importlib.util

from pathlib import Path


def get_python_files(src='step_definitions'):
    folder_path = Path(src)
    py_files = [str(file) for file in folder_path.glob("**/*.py")]
    return py_files


def import_module_from_file(module_name_to_import, py_path):
    module_spec = importlib.util.spec_from_file_location(module_name_to_import, py_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
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
