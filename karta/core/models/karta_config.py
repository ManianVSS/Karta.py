from typing import Optional

import yaml
from pydantic import BaseModel

from karta.core.models.generic import FunctionArgs


class PluginConfig(BaseModel):
    module_name: str
    class_name: str
    args: Optional[list] = []
    kwargs: Optional[dict] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class KartaConfig(BaseModel):
    property_files: Optional[list[str]] = []
    dependency_injector: Optional[PluginConfig] = None
    plugins: Optional[dict[str, PluginConfig]] = {}
    step_runners: Optional[list[str]] = []
    parser_map: Optional[dict] = {}
    test_catalog_manager: Optional[str] = None
    test_lifecycle_hooks: Optional[list[str]] = []
    test_event_listeners: Optional[list[str]] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def read_config_from_file(config_file: str):
    with open(config_file, "r") as stream:
        config_source_str = stream.read()
        config_raw_object = yaml.safe_load(config_source_str)
        config_object = KartaConfig.model_validate(config_raw_object)
        return config_object


default_karta_config = KartaConfig(
    property_files=['properties'],
    dependency_injector=PluginConfig(
        module_name='karta.plugins.dependency_injector',
        class_name='KartaDependencyInjector',
    ),
    plugins={
        'Kriya': PluginConfig(
            module_name='karta.plugins.kriya',
            class_name='Kriya',
            kwargs={
                'feature_directory': 'features',
                'step_def_package': 'step_definitions',
            }
        ),
        'KartaTestCatalogManager': PluginConfig(
            module_name='karta.plugins.catalog',
            class_name='KartaTestCatalogManager',
        ),
        'LoggingTestLifecycleHook': PluginConfig(
            module_name='karta.plugins.listeners',
            class_name='LoggingTestLifecycleHook',
        ),
        'JSONEventDumper': PluginConfig(
            module_name='karta.plugins.listeners',
            class_name='DumpToJSONEventListener',
            kwargs={
                'json_file_name': 'logs/events.json',
            }
        ),
    },
    step_runners=['Kriya', ],
    parser_map={
        '.yml': 'Kriya',
        '.yaml': 'Kriya',
        '.feature': 'Kriya',
        '.kriya': 'Kriya',
    },
    test_catalog_manager='KartaTestCatalogManager',
    test_lifecycle_hooks=['Kriya', 'LoggingTestLifecycleHook', ],
    test_event_listeners=['JSONEventDumper', ],
)
