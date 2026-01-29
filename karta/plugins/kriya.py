import itertools
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Union, Callable, Any, Optional

import yaml

from karta.core.interfaces.plugins import FeatureParser, StepRunner, TestLifecycleHook, DependencyInjector
from karta.core.models.generic import Context
from karta.core.models.test_catalog import Feature, Step
from karta.core.utils import importutils
from karta.core.utils.logger import logger
from karta.parsers.kriya.parser import KriyaParser
from karta.plugins.dependency_injector import Inject
from karta.plugins.step_identifier import StepIdentifier


def step_def(step_identifier):
    def register_step_definition(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in Kriya.step_definition_mapping:
            step_identifier_obj = StepIdentifier(step_identifier_str, func)
            logger.debug("registered %s to %s", str(step_identifier_obj), func.__name__)
            Kriya.step_definition_mapping[step_identifier_str] = step_identifier_obj

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

    step_definition_mapping: dict[str, StepIdentifier] = {}
    # step_definition_backend_mapping: dict[StepIdentifier, Callable] = {}

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
        self.load_step_definitions()

    def load_step_definitions(self):
        # imported_modules = importutils.import_all_modules_in_package(self.step_def_package)
        # # imported_modules = importutils.import_module_from_file(self.step_def_package,
        # #                                                        str(Path(os.getcwd(),
        # #                                                                 *self.step_def_package.split("."))))
        # logger.debug("Imported step definition package: %s", self.step_def_package)
        # self.dependency_injector.inject(*imported_modules)

        # Import step definitions packaging by running exec import statement
        import_statement = f"import {self.step_def_package}"
        # Add current dicectory to sys.path to allow relative imports in step definition modules
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
        exec(import_statement)
        # logger.debug("Locals is %s", locals())
        globals()[self.step_def_package] = locals()[self.step_def_package]

        # logger.debug("Imported step definition package: %s", self.step_def_package)
        # logger.debug("Global step defintion paackage module exists: %s", self.step_def_package in globals().keys())

        # Search for python modules in step definitions folder
        step_definition_module_python_files = importutils.get_python_files(self.step_def_package)
        # # Scan for each python module if it has step definitions, add them to step definition mapping
        for py_file in step_definition_module_python_files:
            module_name = Path(py_file).stem  # os.path.split(py_file)[-1].strip(".py")
            imported_module = importutils.import_module_from_file(module_name, py_file)
            self.dependency_injector.inject(imported_module)

    def parse_feature(self, feature_source: str, yaml_parser: bool = False) -> Feature:
        if yaml_parser:
            # If yaml_parser is True, parse the feature source as YAML
            feature_raw_object = yaml.safe_load(feature_source)
            feature_object = Feature.model_validate(feature_raw_object)
            return feature_object
        else:
            feature_object = self.parser.parse(feature_source)
            return feature_object

    def parse_feature_file(self, feature_file: str) -> Feature:
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

    def get_features(self, ) -> list[Feature]:
        parsed_features = []
        folder_path = Path(self.feature_directory)
        for file in itertools.chain(folder_path.glob("**/*.yaml"), folder_path.glob("**/*.feature"),
                                    folder_path.glob("**/*.kriya")):
            parsed_feature = self.parse_feature_file(str(file))
            parsed_features.append(parsed_feature)
        return parsed_features

    def get_steps(self) -> list[str]:
        return [*self.step_definition_mapping.keys()]

    # TODO: Make step registry hanlde step mapping and parsing
    def is_step_available(self, name: str) -> bool:
        if name in self.step_definition_mapping.keys():
            return True
        matching_step_definition_function, parameters = self.get_matching_step_implementation(name)

        return matching_step_definition_function is not None

    def get_matching_step_implementation(self, step_text: str) -> tuple[Optional[
        Callable[[dict, ...], Union[None, bool, dict, tuple[bool, dict]]]], list]:
        # Iterate through step definition to match text
        for step_definition_obj in self.step_definition_mapping.values():
            match_result, match_parameters = step_definition_obj.match(step_text)
            if match_result:
                return step_definition_obj.backend_function, match_parameters
        return None, []

    def run_step(self, test_step: Step, context: dict) -> Union[tuple[dict, bool, str], bool]:
        step_to_call = test_step.identifier.strip()
        # if step_to_call in self.step_definition_mapping.keys():
        try:
            matching_step_definition_function, parameters = self.get_matching_step_implementation(step_to_call)

            if not matching_step_definition_function:
                message = "Step definition mapping for {} could not be found".format(step_to_call)
                return {}, False, message
            return matching_step_definition_function(context, *parameters)
            # return step_result, True, None
        except Exception as e:
            return {}, False, str(e) + "\n" + traceback.format_exc()

    # else:
    #     message = "Step definition mapping for {} could not be found".format(step_to_call)
    #     return {}, False, message

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
