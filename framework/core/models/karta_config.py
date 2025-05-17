from typing import Optional

import yaml
from pydantic import BaseModel

from framework.core.models.generic import FunctionArgs


class PluginConfig(BaseModel):
    module_name: str
    class_name: str
    init: Optional[FunctionArgs] = None

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
        module_name='framework.plugins.dependency_injector',
        class_name='KartaDependencyInjector',
    ),
    plugins={
        'Kriya': PluginConfig(
            module_name='framework.plugins.kriya',
            class_name='Kriya',
            init=FunctionArgs(
                args=[],
                kwargs={
                    'feature_directory': 'features',
                    'step_def_package': 'step_definitions',
                }
            )
        ),
        'KriyaGherkin': PluginConfig(
            module_name='framework.plugins.kriya',
            class_name='KriyaGherkinPlugin',
            init=FunctionArgs(
                args=[],
                kwargs={
                    'feature_directory': 'features',
                }
            )
        ),
        'KartaTestCatalogManager': PluginConfig(
            module_name='framework.plugins.catalog',
            class_name='KartaTestCatalogManager',
        ),
        'LoggingTestLifecycleHook': PluginConfig(
            module_name='framework.plugins.listeners',
            class_name='LoggingTestLifecycleHook',
        ),
        'JSONEventDumper': PluginConfig(
            module_name='framework.plugins.listeners',
            class_name='DumpToJSONEventListener',
            init=FunctionArgs(
                args=[],
                kwargs={
                    'json_file_name': 'logs/events.json',
                }
            )
        ),
    },
    step_runners=['Kriya', ],
    parser_map={
        '.yml': 'Kriya',
        '.yaml': 'Kriya',
        '.feature': 'KriyaGherkin',
        '.kriya': 'KriyaGherkin',
    },
    test_catalog_manager='KartaTestCatalogManager',
    test_lifecycle_hooks=['Kriya', 'LoggingTestLifecycleHook', ],
    test_event_listeners=['JSONEventDumper', ],
)
