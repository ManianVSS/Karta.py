from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field

from framework.core.models.test_catalog import TestNode, TestScenario
from framework.core.utils.datautils import get_empty_list


class ResultNode(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    line_number: Optional[int] = 0


class StepResult(ResultNode):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    results: Optional[Dict] = None
    step_results: Optional[list['StepResult']] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful

    def merge_result(self, another):
        if not self.start_time:
            self.start_time = another.start_time
        if another.end_time:
            self.end_time = another.end_time

        if not self.error:
            self.error = another.error
        self.successful = not self.error and self.successful and another.successful
        if another.results:
            self.results.update(another.results)

    def add_step_result(self, step_result: 'StepResult'):
        if self.step_results is None:
            self.step_results = []
        self.step_results.append(step_result)
        if not self.error:
            self.error = step_result.error
        self.successful = not self.error and self.successful and step_result.successful



class ScenarioResult(ResultNode):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    step_results: Optional[list[StepResult]] = Field(default_factory=get_empty_list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful

    def add_step_result(self, step_result: StepResult):
        if self.step_results is None:
            self.step_results = []
        self.step_results.append(step_result)
        if not self.error:
            self.error = step_result.error
        self.successful = not self.error and self.successful and step_result.successful


class FeatureResult(ResultNode):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    scenario_results: Optional[list[ScenarioResult]] = Field(default_factory=get_empty_list)
    _line_number: Optional[int] = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful

    def add_scenario_result(self, scenario_result: ScenarioResult):
        if self.scenario_results is None:
            self.scenario_results = []
        self.scenario_results.append(scenario_result)
        if not self.error:
            self.error = scenario_result.error
        self.successful = not self.error and self.successful and scenario_result.successful


class Run(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    scenarios: Optional[set[TestScenario]] = Field(default_factory=get_empty_list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RunResult(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    feature_results: Optional[list[FeatureResult]] = Field(default_factory=get_empty_list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful

    def add_feature_result(self, feature_result: FeatureResult):
        if self.feature_results is None:
            self.feature_results = []
        self.feature_results.append(feature_result)
        if not self.error:
            self.error = feature_result.error
        self.successful = not self.error and self.successful and feature_result.successful
