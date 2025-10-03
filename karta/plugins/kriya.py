import itertools
import re
import traceback
from pathlib import Path
from typing import Union, Callable

import yaml

from karta.core.interfaces.lifecycle import TestLifecycleHook, DependencyInjector
from karta.core.interfaces.test_interfaces import FeatureParser, StepRunner
from karta.core.models.generic import Context
from karta.core.models.test_catalog import TestFeature, TestStep
from karta.core.utils import importutils
from karta.core.utils.logger import logger
from karta.parsers.kriya.parser import KriyaParser
from karta.plugins.dependency_injector import Inject


def step_def(step_identifier):
    def register_step_definition(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in Kriya.step_definition_mapping:
            logger.debug("registering %s to %s", step_identifier_str, func.__name__)
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


def before_run(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_before_run(func):

        if tag_match_regex not in Kriya.before_run_mapping.keys():
            Kriya.before_run_mapping[tag_match_regex] = []

        logger.debug("registering hook before run %s", str(tag_match_regex))
        Kriya.before_run_mapping[tag_match_regex].append(func)

        return func

    return register_before_run


def before_feature(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_before_feature(func):

        if tag_match_regex not in Kriya.before_feature_mapping.keys():
            Kriya.before_feature_mapping[tag_match_regex] = []

        logger.debug("registering hook before feature %s", str(tag_match_regex))
        Kriya.before_feature_mapping[tag_match_regex].append(func)

        return func

    return register_before_feature


def before_feature_iteration(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_before_feature_iteration(func):

        if tag_match_regex not in Kriya.before_feature_iteration_mapping.keys():
            Kriya.before_feature_iteration_mapping[tag_match_regex] = []

        logger.debug("registering hook before feature_iteration %s", str(tag_match_regex))
        Kriya.before_feature_iteration_mapping[tag_match_regex].append(func)

        return func

    return register_before_feature_iteration


def before_scenario(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_before_scenario(func):

        if tag_match_regex not in Kriya.before_scenario_mapping.keys():
            Kriya.before_scenario_mapping[tag_match_regex] = []

        logger.debug("registering hook before scenario %s", str(tag_match_regex))
        Kriya.before_scenario_mapping[tag_match_regex].append(func)

        return func

    return register_before_scenario


def after_scenario(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_after_scenario(func):

        if tag_match_regex not in Kriya.after_scenario_mapping.keys():
            Kriya.after_scenario_mapping[tag_match_regex] = []

        logger.debug("registering hook after scenario %s", str(tag_match_regex))
        Kriya.after_scenario_mapping[tag_match_regex].append(func)

        return func

    return register_after_scenario


def after_feature_iteration(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_after_feature_iteration(func):

        if tag_match_regex not in Kriya.after_feature_iteration_mapping.keys():
            Kriya.after_feature_iteration_mapping[tag_match_regex] = []

        logger.debug("registering hook after feature_iteration %s", str(tag_match_regex))
        Kriya.after_feature_iteration_mapping[tag_match_regex].append(func)

        return func

    return register_after_feature_iteration


def after_feature(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_after_feature(func):

        if tag_match_regex not in Kriya.after_feature_mapping.keys():
            Kriya.after_feature_mapping[tag_match_regex] = []

        logger.debug("registering hook after feature %s", str(tag_match_regex))
        Kriya.after_feature_mapping[tag_match_regex].append(func)

        return func

    return register_after_feature


def after_run(tag_match_regex=None):
    if (tag_match_regex is not None) and not isinstance(tag_match_regex, str):
        raise TypeError("tag_match_regex must be a regex string")

    if tag_match_regex is None:
        tag_match_regex = '.*'

    def register_after_run(func):

        if tag_match_regex not in Kriya.after_run_mapping.keys():
            Kriya.after_run_mapping[tag_match_regex] = []

        logger.debug("registering hook after run %s", str(tag_match_regex))
        Kriya.after_run_mapping[tag_match_regex].append(func)

        return func

    return register_after_run


def check_and_run_hooks(context: Context, hook_mapping: dict[str, list[Callable]], tags: list[str], hook_type: str):
    for tag_match_regex, hooks in hook_mapping.items():
        if any(re.match(tag_match_regex, tag) for tag in tags):
            for hook in hooks:
                try:
                    logger.info("Running %s hook %s", hook_type, hook.__name__)
                    hook(context)
                except Exception as e:
                    logger.error("Error running %s hook %s: %s", hook_type, hook.__name__, str(e))
                    raise e


class Kriya(FeatureParser, StepRunner, TestLifecycleHook):
    dependency_injector: DependencyInjector = Inject()

    step_definition_mapping: dict[str, Callable] = {}

    before_run_mapping: dict[str, list[Callable]] = {}
    before_feature_mapping: dict[str, list[Callable]] = {}
    before_feature_iteration_mapping: dict[str, list[Callable]] = {}
    before_scenario_mapping: dict[str, list[Callable]] = {}
    after_scenario_mapping: dict[str, list[Callable]] = {}
    after_feature_iteration_mapping: dict[str, list[Callable]] = {}
    after_feature_mapping: dict[str, list[Callable]] = {}
    after_run_mapping: dict[str, list[Callable]] = {}

    def __init__(self, feature_directory: str, step_def_package: str):
        self.parser = KriyaParser()
        self.feature_directory = feature_directory
        self.step_def_package = step_def_package

    def __post_inject__(self):
        # imported_modules = importutils.import_all_modules_in_package(self.step_def_package)
        # # imported_modules = importutils.import_module_from_file(self.step_def_package,
        # #                                                        str(Path(os.getcwd(),
        # #                                                                 *self.step_def_package.split("."))))
        # logger.info("Imported step definition package: %s", self.step_def_package)
        # self.dependency_injector.inject(*imported_modules)

        # Search for python modules in step definitions folder
        step_definition_module_python_files = importutils.get_python_files(self.step_def_package)
        # Scan for each python module if it has step definitions, add them to step definition mapping
        for py_file in step_definition_module_python_files:
            module_name = Path(py_file).stem  # os.path.split(py_file)[-1].strip(".py")
            imported_module = importutils.import_module_from_file(module_name, py_file)
            self.dependency_injector.inject(imported_module)

    def parse_feature(self, feature_source: str, yaml_parser: bool = False) -> TestFeature:
        if yaml_parser:
            # If yaml_parser is True, parse the feature source as YAML
            feature_raw_object = yaml.safe_load(feature_source)
            feature_object = TestFeature.model_validate(feature_raw_object)
            return feature_object
        else:
            feature_object = self.parser.parse(feature_source)
            return feature_object

    def parse_feature_file(self, feature_file: str) -> TestFeature:
        if feature_file.endswith(".yaml") or feature_file.endswith(".yml"):
            with open(feature_file, "r") as stream:
                parsed_feature = self.parse_feature(stream.read(), yaml_parser=True)
                # str(Path(feature_file).resolve())
                parsed_feature.source = feature_file
                return parsed_feature
        else:
            with open(feature_file, "r") as stream:
                parsed_feature = self.parse_feature(stream.read())
                # str(Path(feature_file).resolve())
                parsed_feature.set_source(feature_file)
                return parsed_feature

    def get_features(self, ) -> list[TestFeature]:
        parsed_features = []
        folder_path = Path(self.feature_directory)
        for file in itertools.chain(folder_path.glob("**/*.yaml"), folder_path.glob("**/*.feature"),
                                    folder_path.glob("**/*.kriya")):
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

    def run_start(self, context: Context):
        run_name = context.run_info.run.name
        check_and_run_hooks(context, self.before_run_mapping, [run_name], "before run")

    def feature_start(self, context: Context):
        feature_tags = context.run_info.feature.tags
        check_and_run_hooks(context, self.before_feature_mapping, feature_tags, "before feature")

    def feature_iteration_start(self, context: Context):
        feature_tags = context.run_info.feature.tags
        check_and_run_hooks(context, self.before_feature_iteration_mapping, feature_tags, "before feature iteration")

    def scenario_start(self, context: Context):
        # feature_tags = context.run_info.feature.tags
        scenario_tags = context.run_info.scenario.tags
        # feature_tags | scenario_tags
        check_and_run_hooks(context, self.before_scenario_mapping, scenario_tags, "before scenario")

    def step_start(self, context: Context):
        pass

    def step_complete(self, context: Context):
        pass

    def scenario_complete(self, context: Context):
        # feature_tags = context.run_info.feature.tags
        scenario_tags = context.run_info.scenario.tags
        # feature_tags | scenario_tags
        check_and_run_hooks(context, self.after_scenario_mapping, scenario_tags, "after scenario")

    def feature_iteration_complete(self, context: Context):
        feature_tags = context.run_info.feature.tags
        check_and_run_hooks(context, self.after_feature_iteration_mapping, feature_tags, "after feature iteration")

    def feature_complete(self, context: Context):
        feature_tags = context.run_info.feature.tags
        check_and_run_hooks(context, self.after_feature_mapping, feature_tags, "after feature")

    def run_complete(self, context: Context):
        run_name = context.run_info.run.name
        check_and_run_hooks(context, self.after_run_mapping, [run_name], "after run")
