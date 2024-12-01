import itertools
from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field

from framework.core.utils.datautils import get_empty_list


class TestNode(BaseModel):
    name: str
    _source: Optional[str] = None
    _line_number: Optional[int] = 0
    _parent: 'Optional[TestNode]' = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __hash__(self):
        return id(self)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @parent.deleter
    def parent(self):
        del self._parent

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @source.deleter
    def source(self):
        del self._source

    @property
    def line_number(self):
        return self._line_number

    @line_number.setter
    def line_number(self, value):
        self._line_number = value

    @line_number.deleter
    def line_number(self):
        del self._line_number


class TestStep(TestNode):
    conjunction: Optional[str] = None
    # positional_parameters: Optional[list] = []
    data: Optional[Dict] = None
    text: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @TestNode.source.setter
    def source(self, source: str):
        self._source = source

    @TestNode.parent.setter
    def parent(self, parent: 'TestScenario|TestFeature'):
        self._parent = parent


class StepResult(TestNode):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    results: Optional[Dict] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    setup_steps: Optional[list[TestStep]] = Field(default_factory=get_empty_list)
    steps: list[TestStep]
    teardown_steps: Optional[list[TestStep]] = Field(default_factory=get_empty_list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if 'source' in kwargs.keys():
            self.source = kwargs['source']

    @TestNode.source.setter
    def source(self, source: str):
        self._source = source

        for step in itertools.chain(self.setup_steps, self.steps, self.teardown_steps):
            step.source = source

    @TestNode.parent.setter
    def parent(self, parent: 'TestFeature'):
        self._parent = parent
        for step in itertools.chain(self.setup_steps, self.steps, self.teardown_steps):
            step.parent = self


class ScenarioResult(TestNode):
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
        self.error = self.error or step_result.error
        self.successful = not self.error and self.successful and step_result.successful


class TestFeature(TestNode):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    setup_steps: Optional[list[TestStep]] = Field(default_factory=get_empty_list)
    scenarios: set[TestScenario]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if 'source' in kwargs.keys():
            self.source = kwargs['source']

        self.set_parent()

    @TestNode.source.setter
    def source(self, source: str):
        self._source = source

        if self.setup_steps:
            for setup_step in self.setup_steps:
                setup_step.source = source

        if self.scenarios:
            for scenario in self.scenarios:
                scenario.source = source

    def set_parent(self):

        if self.setup_steps:
            for setup_step in self.setup_steps:
                setup_step.parent = self

        if self.scenarios:
            for scenario in self.scenarios:
                scenario.parent = self


class FeatureResult(TestNode):
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
        self.error = self.error or scenario_result.error
        self.successful = not self.error and self.successful and scenario_result.successful
