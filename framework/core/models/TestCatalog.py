from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel


class TestNode(BaseModel):
    line_number: Optional[int] = None


class TestStep(TestNode):
    conjunction: Optional[str] = None
    name: str
    # positional_parameters: Optional[list] = []
    data: Optional[Dict] = None
    text: Optional[str] = None


class StepResult(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    results: Optional[Dict] = None

    def is_successful(self):
        return not self.error and self.successful

    def merge_result(self, another):
        if not self.start_time:
            self.start_time = another.start_time
        if another.end_time:
            self.end_time = another.end_time
        self.error = self.error or another.error
        self.successful = not self.error and self.successful and another.successful
        if another.results:
            self.results.update(another.results)


class TestScenario(TestNode):
    name: str
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    # setup_steps: Optional[list[TestStep]]
    steps: list[TestStep]
    # teardown_steps: Optional[list[TestStep]]


class ScenarioResult(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    step_results: Optional[list[StepResult]] = []

    def is_successful(self):
        return not self.error and self.successful

    def add_step_result(self, step_result: StepResult):
        if self.step_results is None:
            self.step_results = []
        self.step_results.append(step_result)
        self.error = self.error or step_result.error
        self.successful = not self.error and self.successful and step_result.successful


class TestFeature(TestNode):
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
