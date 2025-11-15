import abc
from importlib import import_module
from typing import Optional, TypeVar, Type

from pydantic import BaseModel


class PluginConfig(BaseModel):
    module_name: str
    class_name: str
    args: Optional[list] = []
    kwargs: Optional[dict] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Plugin(metaclass=abc.ABCMeta):
    pass


PLUGIN_CLASS = TypeVar('PLUGIN_CLASS', bound=Plugin)


def get_plugin_from_config(plugin_config: PluginConfig, plugin_base_class: Type[PLUGIN_CLASS] = None) -> PLUGIN_CLASS:
    plugin_module = import_module(plugin_config.module_name)

    plugin_class = getattr(plugin_module, plugin_config.class_name, None)

    if plugin_base_class and not issubclass(plugin_class, plugin_base_class):
        raise Exception(
            f"Plugin class {plugin_config.class_name} in module {plugin_config.module_name} is not a subclass of {plugin_base_class.__name__}"
        )

    args = plugin_config.args if plugin_config.args else []
    kwargs = plugin_config.kwargs if plugin_config.kwargs else {}

    # Check if the plugin class is found
    if not plugin_class:
        raise Exception(
            f"Plugin class {plugin_config.class_name} not found in module {plugin_config.module_name}")

    # Check that the plugin class is a subclass of Plugin
    if not issubclass(plugin_class, Plugin):
        raise Exception(
            f"Plugin class {plugin_config.class_name} in module {plugin_config.module_name} is not a subclass of Plugin")

    # Create an instance of the plugin class with the provided arguments
    try:
        # noinspection PyArgumentList
        plugin = plugin_class(*args, **kwargs)
    except Exception as e:
        raise Exception(
            f"Failed to create plugin instance {plugin_config.class_name} from module {plugin_config.module_name}: {str(e)}")

    # Check if the plugin is an instance of Plugin
    if not isinstance(plugin, Plugin):
        raise Exception(f"Plugin {plugin_config.class_name} is not an instance of Plugin")

    return plugin


class DependencyInjector(Plugin):
    @abc.abstractmethod
    def register(self, name: str, value: object) -> object:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, *list_of_objects) -> bool:
        raise NotImplementedError
