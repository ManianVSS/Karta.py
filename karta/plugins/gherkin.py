from pathlib import Path

from karta.core.models.plugins import FeatureParser
from karta.core.models.test_catalog import TestFeature
from karta.parsers.gherkin.parser import GherkinParser


class GherkinPlugin(FeatureParser):
    step_definition_mapping = {}

    def __init__(self, feature_directory: str):
        self.parser = GherkinParser()
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
        for file in folder_path.glob("**/*.feature"):
            parsed_feature = self.parse_feature_file(str(file))
            parsed_features.append(parsed_feature)
        return parsed_features


gherkin_plugin = GherkinPlugin(feature_directory='features')
