from inspect import getmodule
from pathlib import Path
from types import ModuleType

from karta.core.utils import importutils
from karta.core.utils.logger import logger
from karta.plugins import kriya, dependency_injector
from karta.runner import karta_main

_plugin_modules: dict[str, ModuleType] = {
    "karta.plguins.dependency_injector": dependency_injector,
    "karta.plguins.kriya": kriya,
}


def register_module(plugin_module: ModuleType):
    logger.info("Registering plugin module {}".format(str(plugin_module.__name__)))

    # parent_module = getmodule(plugin_module)
    # if parent_module:
    #     register_module(parent_module)
    if plugin_module.__name__ not in _plugin_modules:
        _plugin_modules[plugin_module.__name__] = plugin_module


def register_plugin(plugin_class):
    logger.info("Registering plugin object {}".format(str(plugin_class)))
    plugin_module = getmodule(plugin_class)
    register_module(plugin_module)


step_def_package = "step_definitions"
step_definition_module_python_files = importutils.get_python_files(step_def_package)
# Scan for each python module if it has step definitions, add them to step definition mapping
for py_file in step_definition_module_python_files:
    module_name = Path(py_file).stem  # os.path.split(py_file)[-1].strip(".py")
    imported_module = importutils.import_module_from_file(module_name, py_file)
    register_module(imported_module)

if __name__ == '__main__':
    karta_main()
