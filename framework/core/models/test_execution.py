from datetime import datetime
from typing import Optional, Dict, Union

from pydantic import BaseModel

from framework.core.models.test_catalog import TestScenario
from framework.core.utils.datautils import serialize_exception


class ResultNode(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    line_number: Optional[int] = 0


class TestIncident(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    tags: Optional[set[str]] = None
    exception: Optional[Union[dict, str]] = None
    time_of_occurrence: Optional[datetime] = datetime.now()

    def __init__(self, **kwargs):
        if 'exception' in kwargs and isinstance(kwargs['exception'], Exception):
            kwargs['exception'] = serialize_exception(kwargs['exception'])
        super().__init__(**kwargs)


class StepResult(ResultNode):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    results: Optional[Dict] = None
    step_results: Optional[list['StepResult']] = None
    incidents: Optional[list[TestIncident]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful and not self.incidents

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

        if another.incidents:
            if self.incidents is None:
                self.incidents = []
            self.incidents.extend(another.incidents)

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
    step_results: Optional[list[StepResult]] = []
    iteration_index: Optional[int] = 1

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
    iterations_count: Optional[int] = 1
    failed_iterations: Optional[list[int]] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful

    def add_scenario_result(self, scenario_result: ScenarioResult, iteration_index: Optional[int] = 1):
        if not self.error:
            self.error = scenario_result.error
        if not scenario_result.is_successful() and iteration_index not in self.failed_iterations:
            self.failed_iterations.append(iteration_index)
        self.successful = not self.error and self.successful and scenario_result.successful

    def add_iteration_result(self, scenario_results: list[ScenarioResult]):
        for scenario_result in scenario_results:
            self.add_scenario_result(scenario_result)


class Run(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    scenarios: Optional[set[TestScenario]] = set()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RunResult(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    feature_results: Optional[list[FeatureResult]] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_successful(self):
        return not self.error and self.successful

    def add_feature_result(self, feature_result: FeatureResult):
        if self.feature_results is None:
            self.feature_results = []
        self.feature_results.append(feature_result)
