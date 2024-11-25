import itertools
import pathlib
import traceback
from datetime import datetime
from pathlib import Path
from types import NoneType

import yaml

from framework.core.interfaces.test_interfaces import StepRunner, FeatureParser
from framework.core.models.generic import Context
from framework.core.models.karta_config import KartaConfig, default_karta_config, PluginConfig
from framework.core.models.test_catalog import TestFeature, FeatureResult, ScenarioResult, StepResult, TestStep, \
    TestScenario
from importlib import import_module


class KartaRuntime:
    config: KartaConfig = default_karta_config
    plugins: dict[str, StepRunner | FeatureParser] = {}
    step_runners: list[StepRunner] = []
    parser_map: dict[str, FeatureParser] = {}

    def __init__(self, config: KartaConfig = default_karta_config):
        self.load_config(config)

    def load_config(self, config: KartaConfig = default_karta_config):
        self.config = config
        self.plugins.clear()
        for plugin_name, plugin_config in self.config.plugins.items():
            plugin_module = import_module(plugin_config.module_name)
            plugin_class = getattr(plugin_module, plugin_config.class_name)
            plugin = plugin_class(*plugin_config.init.args, **plugin_config.init.kwargs)
            self.plugins[plugin_name] = plugin

        self.step_runners.clear()
        for step_runner_name in self.config.step_runners:
            plugin = self.plugins[step_runner_name]
            if not isinstance(plugin, StepRunner):
                raise Exception("Passed plugin is not a step runner" + str(plugin.__class__))
            self.step_runners.append(plugin)

        self.parser_map.clear()
        for extension, feature_parser_name in self.config.parser_map.items():
            if feature_parser_name not in self.plugins.keys():
                raise Exception("Unknown feature source parser plugin name " + feature_parser_name)
            plugin = self.plugins[feature_parser_name]
            if not isinstance(plugin, FeatureParser):
                raise Exception("Passed plugin is not a feature parser" + str(plugin.__class__))
            self.parser_map[extension] = self.plugins[feature_parser_name]

    def run_feature_file(self, feature_file, base_context=None):
        # Load the feature file to run
        if base_context is None:
            base_context = Context()
        feature_file_extn = pathlib.Path(feature_file).suffix
        if feature_file_extn not in self.parser_map.keys():
            raise Exception("Unknown feature file type")
        feature = self.parser_map[feature_file_extn].parse_feature_file(feature_file)
        return self.run_feature(feature, base_context=base_context)

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
        print('Running step ', str(step.name))
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

    def run_scenario(self, scenario: TestScenario, base_context: Context, ):
        if base_context is None:
            base_context = Context()
        scenario_result = ScenarioResult(name=scenario.name, )
        scenario_result.source = scenario.source
        scenario_result.line_number = scenario.line_number
        scenario_result.start_time = datetime.now()
        context = Context(**base_context)
        print('Running scenario ', str(scenario.name))
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

    def run_feature(self, feature: TestFeature, base_context=None):
        if base_context is None:
            base_context = Context()
        feature_result = FeatureResult(name=feature.name)
        feature_result.source = feature.source
        feature_result.line_number = feature.line_number
        feature_result.start_time = datetime.now()
        print('Running feature ', str(feature.name))
        for scenario in feature.scenarios:
            scenario_result = self.run_scenario(scenario, base_context, )
            scenario_result._parent = feature_result
            feature_result.add_scenario_result(scenario_result)
        feature_result.end_time = datetime.now()
        return feature_result

    def filter_with_tags(self, features: str, tags: [str]):
        raise NotImplementedError


config_file_path = Path('karta_config.yaml')
karta_config = default_karta_config

if config_file_path.exists():
    with open(config_file_path, "r") as stream:
        config_yaml_string = stream.read()
        karta_config_raw = yaml.safe_load(config_yaml_string)
        karta_config = KartaConfig.model_validate(karta_config_raw)

karta_runtime = KartaRuntime(config=karta_config)
