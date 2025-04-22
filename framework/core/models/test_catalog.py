import itertools
from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel


class TestNode(BaseModel):
    name: Optional[str] = None
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


class StepType(Enum):
    STEP = 0
    CONDITION = 1
    LOOP = 2


class TestStep(TestNode):
    conjunction: Optional[str] = None
    # positional_parameters: Optional[list] = []
    type: Optional[StepType] = StepType.STEP
    data: Optional[Dict] = None
    # text: Optional[str] = None
    steps: Optional[list['TestStep']] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @TestNode.source.setter
    def source(self, source: str):
        self._source = source

    @TestNode.parent.setter
    def parent(self, parent: 'TestScenario|TestFeature'):
        self._parent = parent


class TestScenario(TestNode):
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    setup_steps: Optional[list[TestStep]] = []
    steps: list[TestStep]
    teardown_steps: Optional[list[TestStep]] = []
    probability: Optional[float] = 1.0

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


class TestFeature(TestNode):
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    setup_steps: Optional[list[TestStep]] = []
    scenarios: set[TestScenario]
    number_of_iterations: Optional[int] = 1

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


class IterationPolicy(Enum):
    ALL_PER_ITERATION = 0
    ONE_PER_ITERATION = 1


class FeatureExecutionProfile(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scenarios: Optional[list[str]] = []
    number_of_iterations: Optional[int] = 1
    iteration_policy: Optional[IterationPolicy] = IterationPolicy.ALL_PER_ITERATION
    probability_map: Optional[dict[float, str]] = {}


class TestExecutionProfile(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    features: Optional[list[FeatureExecutionProfile]] = []
    number_of_iterations: Optional[int] = 1
    iteration_policy: Optional[IterationPolicy] = IterationPolicy.ALL_PER_ITERATION
    probability_map: Optional[dict[float, FeatureExecutionProfile]] = {}
