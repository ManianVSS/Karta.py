from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel

from framework.core.models.TestStep import TestStep, StepResult


class TestScenario(BaseModel):
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
