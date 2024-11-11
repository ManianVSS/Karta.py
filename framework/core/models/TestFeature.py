from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel

from framework.core.models.TestScenario import TestScenario, ScenarioResult
from framework.core.models.TestStep import TestStep


class TestFeature(BaseModel):
    name: Optional[str]
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    background_steps: Optional[list[TestStep]] = []
    scenarios: list[TestScenario]


class FeatureResult(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    scenario_results: Optional[list[ScenarioResult]] = []

    def is_successful(self):
        return not self.error and self.successful

    def add_scenario_result(self, scenario_result: ScenarioResult):
        if self.scenario_results is None:
            self.scenario_results = []
        self.scenario_results.append(scenario_result)
        self.error = self.error or scenario_result.error
        self.successful = not self.error and self.successful and scenario_result.successful
