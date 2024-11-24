from typing import Optional, Any

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
    plugins: Optional[dict[str, PluginConfig]] = Field(default_factory=get_empty_dict)
    step_runners: Optional[list[str]] = Field(default_factory=get_empty_list)
    parser_map: Optional[dict] = Field(default_factory=get_empty_dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def read_config_from_file(config_file: str):
    with open(config_file, "r") as stream:
        config_source_str = stream.read()
        config_raw_object = yaml.safe_load(config_source_str)
        config_object = KartaConfig.model_validate(config_raw_object)
        return config_object


default_karta_config = KartaConfig(
    plugins={
        'Kriya': PluginConfig(
            module_name='framework.core.plugins.kriya',
            class_name='Kriya',
            init=FunctionArgs(
                args=[],
                kwargs={
                    'feature_directory': 'features',
                    'step_def_package': 'step_definitions',
                }
            )
        ),
        'Gherkin': PluginConfig(
            module_name='framework.core.plugins.gherkin',
            class_name='GherkinPlugin',
            init=FunctionArgs(
                args=[],
                kwargs={
                    'feature_directory': 'features',
                }
            )
        ),
    },
    step_runners=['Kriya', ],
    parser_map={
        '.yml': 'Kriya',
        '.yaml': 'Kriya',
        '.feature': 'Gherkin',
    }
)
