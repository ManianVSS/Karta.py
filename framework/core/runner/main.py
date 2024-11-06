import importlib
import importlib.util
import inspect
import os
from copy import deepcopy

import yaml

from framework.core.models.Context import Context
from framework.core.models.TestFeature import TestFeature
from framework.core.runner import step_definition_mapping


def load_feature_file(feature_file):
    with open(feature_file, "r") as stream:
        try:
            feature_raw_object = yaml.safe_load(stream)
            feature_object = TestFeature.model_validate(feature_raw_object)
            # feature_object = yaml.load(stream, TestFeature)
            return feature_object
        except yaml.YAMLError as exc:
            print(exc)


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


def init_framework(step_def_package='step_definitions'):
    # Search for python modules in step definitions folder
    step_definition_module_python_files = get_python_files(step_def_package)

    # Scan for each python module if it has step definitions, add them to step definition mapping
    for py_file in step_definition_module_python_files:
        module_name = os.path.split(py_file)[-1].strip(".py")
        imported_step_def_module = dynamic_import(module_name, py_file)
        # for importedObjectName in dir(imported_step_def_module):
        #     import_object = imported_step_def_module.__dict__[importedObjectName]
        #     if callable(import_object):
        #         signature = inspect.signature(import_object)
        #         for k, v in signature.parameters.items():
        #             if k == "__step_def__" and (v.default is not inspect.Parameter.empty):
        #                 step_def_name = v.default
        #                 # if isinstance(step_def_name, str):
        #                 #     step_definition_mapping[step_def_name] = import_object


def run_feature_file(feature_file):
    # Load the feature file to run
    feature = load_feature_file(feature_file)
    return run_feature(feature)


def run_feature(feature: TestFeature):
    result = {}
    print('Running feature ', str(feature.name))
    for scenario in feature.scenarios:
        context = Context()
        print('Running scenario ', str(scenario.name))
        for step in scenario.steps:
            print('Running step ', str(step.name))
            step_to_call = step.name.strip()
            if step_to_call in step_definition_mapping.keys():
                context.feature_name = feature.name
                context.scenario_name = scenario.name
                context.step_name = step.name
                context.step_data = deepcopy(step.data)
                step_definition_mapping[step_to_call](context=context)
            else:
                print("Step definition mapping for %s could not be found", step_to_call)
        result[scenario.name] = context
    return result
