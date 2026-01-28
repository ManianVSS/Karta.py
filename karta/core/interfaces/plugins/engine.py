import abc
from typing import Optional, Union

from karta.core.interfaces.plugins import Plugin
from karta.core.models.test_catalog import Step, Feature, Scenario


class FeatureParser(Plugin):
    @abc.abstractmethod
    def parse_feature(self, feature_source: str) -> Feature:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_feature_file(self, feature_file: str) -> Feature:
        raise NotImplementedError

    @abc.abstractmethod
    def get_features(self, ) -> list[Feature]:
        raise NotImplementedError


class StepRunner(Plugin):
    @abc.abstractmethod
    def get_steps(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def is_step_available(self, name: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def run_step(self, step: Step, context: dict) -> Union[tuple[dict, bool, str], bool]:
        raise NotImplementedError


class TestCatalogManager(Plugin):
    @abc.abstractmethod
    def list_features(self) -> dict[str, Feature]:
        raise NotImplementedError

    @abc.abstractmethod
    def list_scenarios(self) -> list[Scenario]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_features(self, features: list[Feature], ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def add_scenarios(self, scenarios: set[Scenario], ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def filter_with_tags(self, tags: set[str]) -> set[Scenario]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_feature_for_scenario(self, scenario: Scenario) -> Optional[Feature]:
        """
        Get the feature for a given scenario
        :param scenario: The scenario to get the feature for
        :return: The feature for the scenario
        """
        raise NotImplementedError
