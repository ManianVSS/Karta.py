import configparser
import json
import os
from pathlib import Path

import yaml

from karta.core.utils.datautils import deep_update, parse_value


def read_properties(properties_folder: str) -> dict[str, object]:
    properties: dict[str, object] = {}
    folder_path = Path(properties_folder)

    for property_file in folder_path.glob("**/*.ini"):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(property_file)
        source_dict = {}
        for section in config.sections():
            source_dict[section] = {k: parse_value(v) for k, v in config[section].items()}
        deep_update(properties, source_dict)

    for property_file in folder_path.glob("**/*.json"):
        with open(property_file, "r") as stream:
            parsed_properties = json.load(stream)
            deep_update(properties, parsed_properties)

    for property_file in folder_path.glob("**/*.yaml"):
        with open(property_file, "r") as stream:
            parsed_properties = yaml.safe_load(stream.read())
            deep_update(properties, parsed_properties)

    env_properties = {str(k): str(v) for k, v in os.environ.items()}
    # Read only environment variables which have a . or is an existing key
    processed_env_properties = {}
    for env_key, env_value in env_properties.items():
        if not env_key or (env_key == "."):
            continue
        env_key = env_key.strip(".")
        if "." in env_key:
            key_tree = env_key.split(".")
            current_dict = processed_env_properties
            for key in key_tree[:-1]:
                if (key not in current_dict) or not isinstance(current_dict[key], dict):
                    current_dict[key] = {}
                current_dict = current_dict[key]
            current_dict[key_tree[-1]] = parse_value(env_value)
        else:
            if env_key in properties.keys():
                processed_env_properties[env_key] = parse_value(env_value)

    deep_update(properties, processed_env_properties)

    return properties
