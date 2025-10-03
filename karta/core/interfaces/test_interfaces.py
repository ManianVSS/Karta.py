import abc
from typing import Optional

from karta.core.models.test_catalog import TestStep, TestFeature, TestScenario


class Plugin(metaclass=abc.ABCMeta):
    pass


class FeatureParser(Plugin):
    @abc.abstractmethod
    def parse_feature(self, feature_source: str) -> TestFeature:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_feature_file(self, feature_file: str) -> TestFeature:
        raise NotImplementedError

    @abc.abstractmethod
    def get_features(self, ) -> list[TestFeature]:
        raise NotImplementedError


class StepRunner(Plugin):
    @abc.abstractmethod
    def get_steps(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def is_step_available(self, name: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def run_step(self, step: TestStep, context: dict) -> (dict, bool, str):
        raise NotImplementedError


class TestCatalogManager(Plugin):
    @abc.abstractmethod
    def list_features(self) -> dict[str, TestFeature]:
        raise NotImplementedError

    @abc.abstractmethod
    def list_scenarios(self) -> list[TestScenario]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_features(self, features: list[TestFeature], ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def add_scenarios(self, scenarios: set[TestScenario], ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def filter_with_tags(self, tags: set[str]) -> set[TestScenario]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_feature_for_scenario(self, scenario: TestScenario) -> Optional[TestFeature]:
        """
        Get the feature for a given scenario
        :param scenario: The scenario to get the feature for
        :return: The feature for the scenario
        """
        raise NotImplementedError
