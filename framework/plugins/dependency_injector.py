import json
from pathlib import Path
from typing import Optional
import configparser

import yaml

from framework.core.interfaces.test_interfaces import DependencyInjector


class KartaDependencyInjector(DependencyInjector):
    properties: Optional[dict[str, object]] = {}

    def __init__(self, properties_folder: str):
        self.properties = {}
        folder_path = Path(properties_folder)

        for property_file in folder_path.glob("*.ini"):
            config = configparser.RawConfigParser()
            config.read(property_file)
            for section in config.sections():
                self.properties.update({(section + k, v) for k, v in config[section].items()})

        for property_file in folder_path.glob("*.json"):
            with open(property_file, "r") as stream:
                parsed_properties = json.load(stream)
                self.properties.update(parsed_properties)

        for property_file in folder_path.glob("*.yaml"):
            with open(property_file, "r") as stream:
                parsed_properties = yaml.safe_load(stream.read())
                self.properties.update(parsed_properties)

    def inject(self, *list_of_objects: list[object]) -> bool:
        for obj in list_of_objects:
            obj.properties = self.properties
        return True
