from typing import Optional

import yaml
from pydantic import BaseModel, Field

from framework.core.models.generic import FunctionArgs
from framework.core.utils.datautils import get_empty_dict, get_empty_list


class PluginConfig(BaseModel):
    module_name: str
    class_name: str
    init: Optional[FunctionArgs] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class KartaConfig(BaseModel):
    property_files: Optional[list[str]] = Field(default_factory=get_empty_list)
    dependency_injector: Optional[PluginConfig] = None
    plugins: Optional[dict[str, PluginConfig]] = Field(default_factory=get_empty_dict)
    step_runners: Optional[list[str]] = Field(default_factory=get_empty_list)
    parser_map: Optional[dict] = Field(default_factory=get_empty_dict)
    test_catalog_manager: Optional[str] = None
    test_lifecycle_hooks: Optional[list[str]] = Field(default_factory=get_empty_list)
    test_event_listeners: Optional[list[str]] = Field(default_factory=get_empty_list)

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
    test_catalog_manager='Kriya',
    test_lifecycle_hooks=['LoggingTestLifecycleHook', ],
    test_event_listeners=['JSONEventDumper', ],
)
