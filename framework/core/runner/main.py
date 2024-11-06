import importlib
import importlib.util
import inspect
import os
import traceback
from copy import deepcopy
from datetime import datetime
from types import NoneType

import yaml

from framework.core.models.Context import Context
from framework.core.models.TestFeature import TestFeature, FeatureResult
from framework.core.models.TestScenario import ScenarioResult
from framework.core.models.TestStep import StepResult, TestStep
from framework.core.plugins.KriyaPlugin import Kriya


def get_python_files(src='step_definitions'):
    cwd = os.getcwd()
    py_files = []
    for root, dirs, files in os.walk(src):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(cwd, root, file))
    return py_files


def dynamic_import(module_name_to_import, py_path):
    module_spec = importlib.util.spec_from_file_location(module_name_to_import, py_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def dynamic_import_from_src(src, star_import=False):
    my_py_files = get_python_files(src)
    for py_file in my_py_files:
        module_name = os.path.split(py_file)[-1].strip(".py")
        imported_module = dynamic_import(module_name, py_file)
        if star_import:
            for obj in dir(imported_module):
                globals()[obj] = imported_module.__dict__[obj]
        else:
            globals()[module_name] = imported_module
    return


kriya_plugin = Kriya()

default_step_runner = kriya_plugin
default_feature_parser = kriya_plugin


def init_framework(step_def_package='step_definitions'):
    # Search for python modules in step definitions folder
    step_definition_module_python_files = get_python_files(step_def_package)

    # Scan for each python module if it has step definitions, add them to step definition mapping
    for py_file in step_definition_module_python_files:
        module_name = os.path.split(py_file)[-1].strip(".py")
        imported_step_def_module = dynamic_import(module_name, py_file)


def run_feature_file(feature_file):
    # Load the feature file to run
    feature = default_feature_parser.parse_feature_file(feature_file)
    return run_feature(feature)


def run_step(step: TestStep, context: Context):
    print('Running step ', str(step.name))
    step_result = StepResult()
    step_result.name = step.name
    step_result.start_time = datetime.now()
    step_return = default_step_runner.run_step(step, context)

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


def run_feature(feature: TestFeature):
    feature_result = FeatureResult()
    feature_result.name = feature.name
    feature_result.start_time = datetime.now()
    print('Running feature ', str(feature.name))
    for scenario in feature.scenarios:
        scenario_result = ScenarioResult()
        scenario_result.name = scenario.name
        scenario_result.start_time = datetime.now()
        context = Context()
        print('Running scenario ', str(scenario.name))

        for step in scenario.steps:
            try:
                step_result = run_step(step, context)
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
        feature_result.add_scenario_result(scenario_result)
    feature_result.end_time = datetime.now()
    return feature_result
