import itertools
import pathlib
import traceback
from copy import deepcopy
from datetime import datetime
from importlib import import_module
from pathlib import Path
from types import NoneType

import yaml

from framework.core.interfaces.lifecycle import DependencyInjector
from framework.core.interfaces.test_interfaces import StepRunner, FeatureParser, TestCatalogManager
from framework.core.models.generic import Context
from framework.core.models.karta_config import KartaConfig, default_karta_config
from framework.core.models.test_catalog import TestFeature, FeatureResult, ScenarioResult, StepResult, TestStep, \
    TestScenario
from framework.core.utils.datautils import deep_update
from framework.core.utils.logger import logger
from framework.core.utils.properties import read_properties
from framework.plugins.dependency_injector import KartaDependencyInjector


def get_plugin_from_config(plugin_config):
    plugin_module = import_module(plugin_config.module_name)
    plugin_class = getattr(plugin_module, plugin_config.class_name)
    args = plugin_config.init.args if (plugin_config.init and plugin_config.init.args) else []
    kwargs = plugin_config.init.kwargs if (plugin_config.init and plugin_config.init.kwargs) else {}
    plugin = plugin_class(*args, **kwargs)
    return plugin


class KartaRuntime:
    config: KartaConfig = default_karta_config
    properties: dict[str, object] = {}
    dependency_injector: DependencyInjector = None
    plugins: dict[str, StepRunner | FeatureParser | DependencyInjector | TestCatalogManager] = {}
    step_runners: list[StepRunner] = []
    feature_parsers: list[FeatureParser] = []
    parser_map: dict[str, FeatureParser] = {}
    test_catalog_manager: TestCatalogManager = None

    def __init__(self, config: KartaConfig = default_karta_config):
        self.load_config(config)

    def load_config(self, config: KartaConfig = default_karta_config):
        self.config = config
        self.load_properties()
        self.load_dependency_injector()
        self.load_plugins()
        self.load_step_runners()
        self.load_feature_parsers()
        self.load_test_catalog_manager()

    def load_properties(self):
        self.properties = {}
        if self.config.property_files:
            for property_file_name in self.config.property_files:
                properties_read = read_properties(property_file_name)
                deep_update(self.properties, properties_read)

    def load_dependency_injector(self):
        if self.config.dependency_injector:
            plugin = get_plugin_from_config(self.config.dependency_injector)
            if not isinstance(plugin, DependencyInjector):
                raise Exception("Passed plugin is not a DependencyInjector" + str(plugin.__class__))
            self.dependency_injector = plugin
        else:
            self.dependency_injector = KartaDependencyInjector()
        self.dependency_injector.register("karta_runtime", self)
        self.dependency_injector.register("properties", self.properties)

    def load_plugins(self):
        self.plugins.clear()
        for plugin_name, plugin_config in self.config.plugins.items():
            plugin = get_plugin_from_config(plugin_config)
            self.dependency_injector.inject(plugin)
            self.plugins[plugin_name] = plugin

    def load_step_runners(self):
        self.step_runners.clear()
        if not self.config.step_runners or (len(self.config.step_runners) == 0):
            raise Exception("Need at least one step runner configured")
        for step_runner_name in self.config.step_runners:
            plugin = self.plugins[step_runner_name]
            if not isinstance(plugin, StepRunner):
                raise Exception("Passed plugin is not a StepRunner" + str(plugin.__class__))
            if plugin not in self.step_runners:
                self.step_runners.append(plugin)

    def load_feature_parsers(self):
        self.parser_map.clear()
        if not self.config.parser_map or (len(self.config.parser_map) == 0):
            raise Exception("Need at least one feature parser configured")
        for extension, feature_parser_name in self.config.parser_map.items():
            if feature_parser_name not in self.plugins.keys():
                raise Exception("Unknown feature source parser plugin name " + feature_parser_name)
            plugin = self.plugins[feature_parser_name]
            if not isinstance(plugin, FeatureParser):
                raise Exception("Passed plugin is not a FeatureParser" + str(plugin.__class__))
            if plugin not in self.feature_parsers:
                self.feature_parsers.append(plugin)
            self.parser_map[extension] = plugin

    def load_test_catalog_manager(self):
        plugin = self.plugins[self.config.test_catalog_manager]
        if not self.config.test_catalog_manager:
            raise Exception("Need a test catalog manager configured")
        if not isinstance(plugin, TestCatalogManager):
            raise Exception("Passed plugin is not a TestCatalogManager" + str(plugin.__class__))
        self.test_catalog_manager = plugin

        # Add all features from feature parers into test catalog manager
        for feature_parser in self.feature_parsers:
            self.test_catalog_manager.add_features(feature_parser.get_features())

    def run_feature_file(self, feature_file):
        feature_file_extn = pathlib.Path(feature_file).suffix
        if feature_file_extn not in self.parser_map.keys():
            raise Exception("Unknown feature file type")
        feature = self.parser_map[feature_file_extn].parse_feature_file(feature_file)
        return self.run_feature(feature, )

    def run_feature_files(self, feature_files: list[str]):
        feature_results = {}
        for feature_file in feature_files:
            feature_results[feature_file] = self.run_feature_file(feature_file, )
        return feature_results

    def find_step_runner_for_step(self, name: str) -> StepRunner | None:
        for step_runner in self.step_runners:
            if step_runner.is_step_available(name):
                return step_runner
        return None

    def get_steps(self) -> list[str]:
        steps = []
        for step_runner in self.step_runners:
            steps.extend(step_runner.get_steps())
        return steps

    def run_step(self, step: TestStep, context: Context):
        logger.info('Running step %s', str(step.name))
        step_result = StepResult(name=step.name, )
        step_result.source = step.source
        step_result.line_number = step.line_number
        step_result.start_time = datetime.now()

        step_runner = self.find_step_runner_for_step(step.name.strip())
        if step_runner is None:
            raise Exception("Unimplemented step: " + step.name)

        step_return = step_runner.run_step(step, context)

        if not isinstance(step_return, NoneType):
            if isinstance(step_return, dict):
                step_result.results = step_return
            elif isinstance(step_return, tuple):
                if len(step_return) > 0:
                    step_result.results = step_return[0]
                    if len(step_return) > 1:
                        step_result.successful = step_return[1]
                        if len(step_return) > 2:
                            step_result.error = step_return[2]
            else:
                raise Exception("Unprocessable result type: ", type(step_result))

        step_result.end_time = datetime.now()
        return step_result

    def run_scenario(self, scenario: TestScenario, ):
        scenario_result = ScenarioResult(name=scenario.name, )
        scenario_result.source = scenario.source
        scenario_result.line_number = scenario.line_number
        scenario_result.start_time = datetime.now()
        context = Context()
        context.properties = deepcopy(self.properties)
        logger.info('Running scenario %s', str(scenario.name))
        for step in itertools.chain(scenario.parent.setup_steps, scenario.steps):
            try:
                step_result = self.run_step(step, context)
                step_result._parent = scenario_result
                if step_result.results and len(step_result.results) > 0:
                    context.update(step_result.results)
                scenario_result.add_step_result(step_result)
                if not step_result.is_successful():
                    break
            except Exception as e:
                scenario_result.successful = False
                scenario_result.error = str(e) + "\n" + traceback.format_exc()
                break
        scenario_result.end_time = datetime.now()
        return scenario_result

    def run_feature(self, feature: TestFeature, ):
        feature_result = FeatureResult(name=feature.name)
        feature_result.source = feature.source
        feature_result.line_number = feature.line_number
        feature_result.start_time = datetime.now()
        logger.info('Running feature %s', str(feature.name))
        for scenario in feature.scenarios:
            scenario_result = self.run_scenario(scenario, )
            scenario_result._parent = feature_result
            feature_result.add_scenario_result(scenario_result)
        feature_result.end_time = datetime.now()
        return feature_result

    def run_scenarios(self, scenarios: set[TestScenario]) -> list[FeatureResult]:
        feature_to_scenario_map: dict[TestFeature, set[TestScenario]] = {}
        feature_results: list[FeatureResult] = []

        for scenario in scenarios:
            if not scenario.parent:
                raise Exception("Scenario needs to have a parent feature")
            feature = scenario.parent
            if feature not in feature_to_scenario_map.keys():
                feature_to_scenario_map[feature] = set()
            if scenario not in feature_to_scenario_map[feature]:
                feature_to_scenario_map[feature].add(scenario)

        for feature in feature_to_scenario_map.keys():
            feature_result = FeatureResult(name=feature.name)
            feature_result.source = feature.source
            feature_result.line_number = feature.line_number
            feature_result.start_time = datetime.now()
            logger.info('Running feature %s', str(feature.name))
            for scenario in feature_to_scenario_map[feature]:
                scenario_result = self.run_scenario(scenario, )
                scenario_result._parent = feature_result
                feature_result.add_scenario_result(scenario_result)
            feature_result.end_time = datetime.now()
            feature_results.append(feature_result)

        return feature_results

    def filter_with_tags(self, tags: set[str]) -> set[TestScenario]:
        return self.test_catalog_manager.filter_with_tags(tags)

    def run_tags(self, tags: set[str]) -> list[FeatureResult]:
        filtered_scenarios = self.filter_with_tags(tags)
        return self.run_scenarios(filtered_scenarios)


config_file_path = Path('karta_config.yaml')
karta_config = default_karta_config

if config_file_path.exists():
    with open(config_file_path, "r") as stream:
        config_yaml_string = stream.read()
        karta_config_raw = yaml.safe_load(config_yaml_string)
        karta_config = KartaConfig.model_validate(karta_config_raw)

karta_runtime = KartaRuntime(config=karta_config)
