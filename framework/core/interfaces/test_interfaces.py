import abc

from framework.core.models.test_catalog import TestStep, TestFeature, TestScenario


class FeatureParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_feature(self, feature_source: str) -> TestFeature:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_feature_file(self, feature_file: str) -> TestFeature:
        raise NotImplementedError

    @abc.abstractmethod
    def get_feature_files(self, ) -> [str]:
        raise NotImplementedError


class StepRunner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_steps(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def is_step_available(self, name: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def run_step(self, step: TestStep, context: dict) -> (dict, bool, str):
        raise NotImplementedError


class TestCatalogManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load_features(self, feature_directory: str, ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_features(self, feature_directory: str) -> [TestFeature]:
        raise NotImplementedError

    @abc.abstractmethod
    def filter_with_tags(self, features: str, tags: [str]) -> [TestScenario]:
        raise NotImplementedError
