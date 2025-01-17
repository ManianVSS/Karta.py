import itertools
from typing import Optional, Dict

from pydantic import BaseModel, Field

from framework.core.utils.datautils import get_empty_list


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


class TestScenario(TestNode):
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


class TestFeature(TestNode):
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
