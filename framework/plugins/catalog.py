from typing import Optional

from framework.core.interfaces.test_interfaces import TestCatalogManager
from framework.core.models.test_catalog import TestFeature, TestScenario


class KartaTestCatalogManager(TestCatalogManager):
    feature_map: dict[str, set[TestFeature]] = {}
    scenario_map: dict[str, set[TestScenario]] = {}
    scenario_to_feature_map: dict[TestScenario, TestFeature] = {}

    def list_scenarios(self):
        return self.scenario_map

    def list_features(self):
        return self.feature_map

    def add_features(self, features: list[TestFeature], ) -> bool:
        for feature in features:
            if feature.name not in self.feature_map.keys():
                self.feature_map[feature.name] = set()
            self.feature_map[feature.name].add(feature)
            for tag in feature.tags:
                if tag not in self.feature_map.keys():
                    self.feature_map[tag] = set()
                self.feature_map[tag].add(feature)
                if tag not in self.scenario_map.keys():
                    self.scenario_map[tag] = set()
                for scenario in feature.scenarios:
                    self.scenario_to_feature_map[scenario] = feature
                    if scenario not in self.scenario_map[tag]:
                        self.scenario_map[tag].add(scenario)

            self.add_scenarios(feature.scenarios)
        return True

    def add_scenarios(self, scenarios: set[TestScenario], ) -> bool:
        for scenario in scenarios:
            if scenario.name not in self.scenario_map.keys():
                self.scenario_map[scenario.name] = set()
            self.scenario_map[scenario.name].add(scenario)
            for tag in scenario.tags:
                if tag not in self.scenario_map.keys():
                    self.scenario_map[tag] = set()
                if scenario not in self.scenario_map[tag]:
                    self.scenario_map[tag].add(scenario)
        return True

    def filter_with_tags(self, tags: set[str]) -> set[TestScenario]:
        filtered_scenarios = set()
        for tag in tags:
            if tag in self.scenario_map.keys():
                filtered_scenarios.update(self.scenario_map[tag])

        return filtered_scenarios

    def get_feature_for_scenario(self, scenario: TestScenario) -> Optional[TestFeature]:
        """
        Get the feature for a given scenario
        :param scenario: The scenario to get the feature for
        :return: The feature for the scenario
        """
        return self.scenario_to_feature_map.get(scenario, None)
