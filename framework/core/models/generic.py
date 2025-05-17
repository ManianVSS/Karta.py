import json
from copy import deepcopy
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class VarClass(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if name in dict.__dict__.keys():
            return super().__setattr__(name, value)
        self[name] = value
        return value

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def load_from_json(self, json_string: str):
        self.update(json.loads(json_string))

    def load_from_json_file(self, json_file: Path):
        self.load_from_json(json_file.read_text())

    def replace_variables_in_string(self, string_to_process: str, variable_prefix='${', variable_suffix='}'):
        replaced_string = string_to_process

        for variable, value in self.items():
            replaced_string = replaced_string.replace(variable_prefix + variable + variable_suffix, str(value))

        return replaced_string

    def create_copy(self):
        copied_object = VarClass()
        for key, value in self.items():
            if isinstance(value, VarClass):
                copied_object[key] = value.create_copy()
            else:
                copied_object[key] = deepcopy(value)
        return copied_object


class Context(VarClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_copy(self):
        copied_object = Context()
        for key, value in self.items():
            if isinstance(value, VarClass):
                copied_object[key] = value.create_copy()
            else:
                copied_object[key] = deepcopy(value)
        return copied_object


class TestProperties(VarClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_copy(self):
        copied_object = TestProperties()
        for key, value in self.items():
            if isinstance(value, VarClass):
                copied_object[key] = value.create_copy()
            else:
                copied_object[key] = deepcopy(value)
        return copied_object


class FunctionArgs(BaseModel):
    args: Optional[list] = []
    kwargs: Optional[dict] = {}
