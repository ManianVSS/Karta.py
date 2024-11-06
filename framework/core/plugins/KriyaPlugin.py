import traceback
from copy import deepcopy

import yaml

from framework.core.interfaces.FeatureParser import FeatureParser
from framework.core.interfaces.StepRunner import StepRunner
from framework.core.models.TestFeature import TestFeature
from framework.core.models.TestStep import TestStep


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

    def get_steps(self):
        return self.step_definition_mapping

    def parse_feature(self, feature_source: str):
        try:
            feature_raw_object = yaml.safe_load(feature_source)
            feature_object = TestFeature.model_validate(feature_raw_object)
            return feature_object
        except yaml.YAMLError as exc:
            print(exc)

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
            message = "Step definition mapping for %s could not be found".format(step_to_call)
            return {}, False, message

    def parse_feature_file(self, feature_file: str):
        with open(feature_file, "r") as stream:
            return self.parse_feature(stream.read())
