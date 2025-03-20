import json
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

    def __getattribute__(self, name):
        if name in dict.__dict__.keys():
            return super().__getattribute__(name)
        elif name in self.keys():
            return self[name]
        else:
            return None

    def load_from_json(self, json_string: str):
        self.update(json.loads(json_string))

    def load_from_json_file(self, json_file: Path):
        self.load_from_json(json_file.read_text())

    def replace_variables_in_string(self, string_to_process: str, variable_prefix='${', variable_suffix='}'):
        replaced_string = string_to_process

        for variable, value in self.items():
            replaced_string = replaced_string.replace(variable_prefix + variable + variable_suffix, str(value))

        return replaced_string


class Context(VarClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestProperties(VarClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FunctionArgs(BaseModel):
    args: Optional[list] = []
    kwargs: Optional[dict] = {}
