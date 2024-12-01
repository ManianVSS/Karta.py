import abc

from framework.core.models.test_catalog import TestStep, TestFeature, TestScenario


class DependencyInjector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def inject(self, *list_of_objects: list[object]) -> bool:
        raise NotImplementedError


class FeatureParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_feature(self, feature_source: str) -> TestFeature:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_feature_file(self, feature_file: str) -> TestFeature:
        raise NotImplementedError

    @abc.abstractmethod
    def get_features(self, ) -> list[TestFeature]:
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
    def add_features(self, features: list[TestFeature], ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def add_scenarios(self, scenarios: set[TestScenario], ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def filter_with_tags(self, tags: set[str]) -> set[TestScenario]:
        raise NotImplementedError
