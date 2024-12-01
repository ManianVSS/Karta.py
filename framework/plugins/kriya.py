import traceback
from copy import deepcopy
from pathlib import Path

import yaml

from framework.core.interfaces.test_interfaces import FeatureParser, StepRunner, TestCatalogManager
from framework.core.models.test_catalog import TestFeature, TestStep, TestScenario
from framework.core.utils import importutils
from framework.core.utils.logger import logger


def step_def(step_identifier):
    def register_step_definition(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in Kriya.step_definition_mapping:
            logger.info("registering %s", step_identifier_str)
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


class Kriya(FeatureParser, StepRunner, TestCatalogManager):
    step_definition_mapping: dict[str, callable] = {}
    scenario_map: dict[str, set[TestScenario]] = {}

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
            logger.info(exc)

    def parse_feature_file(self, feature_file: str) -> TestFeature:
        with open(feature_file, "r") as stream:
            parsed_feature = self.parse_feature(stream.read())
            # str(Path(feature_file).resolve())
            parsed_feature.source = feature_file
            return parsed_feature

    def get_features(self, ) -> list[TestFeature]:
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

    def add_features(self, features: list[TestFeature], ) -> bool:
        for feature in features:
            for tag in feature.tags:
                if tag not in self.scenario_map.keys():
                    self.scenario_map[tag] = set()
                for scenario in feature.scenarios:
                    if scenario not in self.scenario_map[tag]:
                        self.scenario_map[tag].add(scenario)

            self.add_scenarios(feature.scenarios)
        return True

    def add_scenarios(self, scenarios: set[TestScenario], ) -> bool:
        for scenario in scenarios:
            for tag in scenario.tags:
                if tag not in self.scenario_map.keys():
                    self.scenario_map[tag] = set()
                if scenario not in self.scenario_map[tag]:
                    self.scenario_map[tag].add(scenario)
        return True

    def filter_with_tags(self, tags: set[str]) -> set[TestScenario]:
        filtered_scenarios = set()
        for tag in tags:
            if tag in self.scenario_map.keys():
                filtered_scenarios.update(self.scenario_map[tag])

        return filtered_scenarios
