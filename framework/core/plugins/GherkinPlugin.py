import yaml

from framework.core.interfaces.FeatureParser import FeatureParser
from framework.core.parsers.GkerkinParser.GherkinParser import GherkinParser


class GherkinPlugin(FeatureParser):
    step_definition_mapping = {}

    def __init__(self):
        self.parser = GherkinParser()

    def get_steps(self):
        return self.step_definition_mapping

    def parse_feature(self, feature_source: str):
        try:
            feature_object = self.parser.parse(feature_source)
            return feature_object
        except yaml.YAMLError as exc:
            print(exc)

    def parse_feature_file(self, feature_file: str):
        with open(feature_file, "r") as stream:
            return self.parse_feature(stream.read())
