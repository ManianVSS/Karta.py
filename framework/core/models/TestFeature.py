from framework.core.models.TestScenario import TestScenario


class TestFeature:
    def __init__(self, name=None, scenarios=None):
        self.name = name

        self.scenarios = []
        for scenario in scenarios:
            self.scenarios.append(TestScenario(**scenario))
