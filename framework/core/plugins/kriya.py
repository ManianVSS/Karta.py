import traceback
from copy import deepcopy
from pathlib import Path

import yaml

from framework.core.interfaces.test_interfaces import FeatureParser, StepRunner
from framework.core.models.test_catalog import TestFeature, TestStep
from framework.core.utils import importutils


def step_def(step_identifier):
    def register_step_definition(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in Kriya.step_definition_mapping:
            print("registering ", step_identifier_str)
            Kriya.step_definition_mapping[step_identifier_str] = func

        return func

    return register_step_definition


step_definition = step_def
step = step_def
given = step_def
when = step_def
then = step_def

Given = step_def
When = step_def
Then = step_def


class Kriya(FeatureParser, StepRunner):
    step_definition_mapping = {}

    def __init__(self, feature_directory: str, step_def_package: str):
        self.feature_directory = feature_directory
        # Search for python modules in step definitions folder
        step_definition_module_python_files = importutils.get_python_files(step_def_package)

        # Scan for each python module if it has step definitions, add them to step definition mapping
        for py_file in step_definition_module_python_files:
            module_name = Path(py_file).stem  # os.path.split(py_file)[-1].strip(".py")
            importutils.import_module_from_file(module_name, py_file)

    def parse_feature(self, feature_source: str):
        try:
            feature_raw_object = yaml.safe_load(feature_source)
            feature_object = TestFeature.model_validate(feature_raw_object)
            return feature_object
        except yaml.YAMLError as exc:
            print(exc)

    def parse_feature_file(self, feature_file: str) -> TestFeature:
        with open(feature_file, "r") as stream:
            parsed_feature = self.parse_feature(stream.read())
            # str(Path(feature_file).resolve())
            parsed_feature.source = feature_file
            return parsed_feature

    def get_feature_files(self, ) -> [str]:
        parsed_features = []
        folder_path = Path(self.feature_directory)
        for file in folder_path.glob("*.yaml"):
            parsed_feature = self.parse_feature_file(str(file))
            parsed_features.append(parsed_feature)
        return parsed_features

    def get_steps(self) -> list[str]:
        return [*self.step_definition_mapping.keys()]

    def is_step_available(self, name: str) -> bool:
        return name in self.step_definition_mapping.keys()

    def run_step(self, test_step: TestStep, context: dict):
        step_to_call = test_step.name.strip()
        if step_to_call in self.step_definition_mapping.keys():
            context.step_name = test_step.name
            context.step_data = deepcopy(test_step.data)
            try:
                return self.step_definition_mapping[step_to_call](context=context)
                # return step_result, True, None
            except Exception as e:
                return {}, False, str(e) + "\n" + traceback.format_exc()
        else:
            message = "Step definition mapping for {} could not be found".format(step_to_call)
            return {}, False, message
