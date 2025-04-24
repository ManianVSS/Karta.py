import itertools
import traceback
from pathlib import Path
from typing import Union, Callable

import yaml

from framework.core.interfaces.test_interfaces import FeatureParser, StepRunner, FeatureStore
from framework.core.models.test_catalog import TestFeature, TestStep, TestScenario
from framework.core.utils import importutils
from framework.core.utils.logger import logger
from framework.parsers.kriya.parser import KriyaParser
from framework.plugins.dependency_injector import Inject


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


class Kriya(FeatureParser, StepRunner, FeatureStore):
    dependency_injector = Inject()

    step_definition_mapping: dict[str, Callable] = {}
    feature_map: dict[str, set[TestFeature]] = {}
    scenario_map: dict[str, set[TestScenario]] = {}

    def __init__(self, feature_directory: str, step_def_package: str):
        self.feature_directory = feature_directory
        self.step_def_package = step_def_package

    def __post_inject__(self):
        # Search for python modules in step definitions folder
        step_definition_module_python_files = importutils.get_python_files(self.step_def_package)
        # Scan for each python module if it has step definitions, add them to step definition mapping
        for py_file in step_definition_module_python_files:
            module_name = Path(py_file).stem  # os.path.split(py_file)[-1].strip(".py")
            imported_module = importutils.import_module_from_file(module_name, py_file)
            self.dependency_injector.inject(imported_module)

    def parse_feature(self, feature_source: str):
        feature_raw_object = yaml.safe_load(feature_source)
        feature_object = TestFeature.model_validate(feature_raw_object)
        return feature_object

    def parse_feature_file(self, feature_file: str) -> TestFeature:
        with open(feature_file, "r") as stream:
            parsed_feature = self.parse_feature(stream.read())
            # str(Path(feature_file).resolve())
            parsed_feature.source = feature_file
            return parsed_feature

    def get_features(self, ) -> list[TestFeature]:
        parsed_features = []
        folder_path = Path(self.feature_directory)
        for file in folder_path.glob("**/*.yaml"):
            parsed_feature = self.parse_feature_file(str(file))
            parsed_features.append(parsed_feature)
        return parsed_features

    def get_steps(self) -> list[str]:
        return [*self.step_definition_mapping.keys()]

    def is_step_available(self, name: str) -> bool:
        return name in self.step_definition_mapping.keys()

    def run_step(self, test_step: TestStep, context: dict) -> Union[tuple[dict, bool, str], bool]:
        step_to_call = test_step.name.strip()
        if step_to_call in self.step_definition_mapping.keys():
            try:
                return self.step_definition_mapping[step_to_call](context=context)
                # return step_result, True, None
            except Exception as e:
                return {}, False, str(e) + "\n" + traceback.format_exc()
        else:
            message = "Step definition mapping for {} could not be found".format(step_to_call)
            return {}, False, message

    def list_scenarios(self):
        # catalog = {}
        # for tag, scenarios in self.scenario_map.items():
        #     catalog[tag] = []
        #     for scenario in scenarios:
        #         catalog[tag].append(scenario)
        #         catalog[scenario.name] = scenario
        return self.scenario_map

    def list_features(self):
        return self.feature_map

    def add_features(self, features: list[TestFeature], ) -> bool:
        for feature in features:
            if feature.name not in self.feature_map.keys():
                self.feature_map[feature.name] = set()
            self.feature_map[feature.name].add(feature)
            for tag in feature.tags:
                if tag not in self.feature_map.keys():
                    self.feature_map[tag] = set()
                self.feature_map[tag].add(feature)
                if tag not in self.scenario_map.keys():
                    self.scenario_map[tag] = set()
                for scenario in feature.scenarios:
                    if scenario not in self.scenario_map[tag]:
                        self.scenario_map[tag].add(scenario)

            self.add_scenarios(feature.scenarios)
        return True

    def add_scenarios(self, scenarios: set[TestScenario], ) -> bool:
        for scenario in scenarios:
            if scenario.name not in self.scenario_map.keys():
                self.scenario_map[scenario.name] = set()
            self.scenario_map[scenario.name].add(scenario)
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


class KriyaGherkinPlugin(FeatureParser):
    step_definition_mapping = {}

    def __init__(self, feature_directory: str):
        self.parser = KriyaParser()
        self.feature_directory = feature_directory

    def get_steps(self):
        return self.step_definition_mapping

    def parse_feature(self, feature_source: str) -> TestFeature:
        feature_object = self.parser.parse(feature_source)
        return feature_object

    def parse_feature_file(self, feature_file: str) -> TestFeature:
        with open(feature_file, "r") as stream:
            parsed_feature = self.parse_feature(stream.read())
            # str(Path(feature_file).resolve())
            parsed_feature.source = feature_file
            return parsed_feature

    def get_features(self, ) -> list[TestFeature]:
        parsed_features = []
        folder_path = Path(self.feature_directory)
        for file in itertools.chain(folder_path.glob("**/*.feature"), folder_path.glob("**/*.kriya")):
            parsed_feature = self.parse_feature_file(str(file))
            parsed_features.append(parsed_feature)
        return parsed_features
