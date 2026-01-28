import itertools
from enum import Enum
from random import Random
from typing import Optional

from pydantic import BaseModel

from karta.core.models.testdata import GeneratedObjectValue
from karta.core.utils import randomization_utils


class TestNode(BaseModel):
    source: Optional[str] = None
    line_number: Optional[int] = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __hash__(self):
        return id(self)


class StepType(Enum):
    STEP = 0
    CONDITION = 1
    LOOP = 2


class Step(TestNode):
    conjunction: Optional[str] = None
    identifier: Optional[str] = None
    # positional_parameters: Optional[list] = []
    type: Optional[StepType] = StepType.STEP
    data_rules: Optional[GeneratedObjectValue] = None
    # text: Optional[str] = None
    steps: Optional[list['Step']] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Scenario(TestNode):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    setup_steps: Optional[list[Step]] = []
    steps: list[Step]
    teardown_steps: Optional[list[Step]] = []
    probability: Optional[float] = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_source(self, source: str):
        self.source = source
        for step in itertools.chain(self.setup_steps, self.steps, self.teardown_steps):
            step.source = source

    def validate_scenario(self) -> bool:
        """
        Check if the probability is between greater than 0 and less than equal to 1
        """
        if self.probability:
            return 0 < self.probability <= 1
        return True

class Background(TestNode):
    description: Optional[str] = None
    steps: list[Step]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class IterationPolicy(Enum):
    ALL_PER_ITERATION = "ALL_PER_ITERATION"
    ONE_PER_ITERATION = "ONE_PER_ITERATION"
    SOME_PER_ITERATION = "SOME_PER_ITERATION"


class Rule(TestNode):
    name: Optional[str] = None
    description: Optional[str] = None
    background: Optional[Background] = None
    scenarios: Optional[set[Scenario]] = set()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Feature(TestNode):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[set[str]] = None
    background: Optional[Background] = None
    scenarios: Optional[set[Scenario]] = set()
    rules: Optional[set[Rule]] = set()
    iterations: Optional[int] = 1
    iteration_policy: Optional[IterationPolicy] = IterationPolicy.ALL_PER_ITERATION

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_source(self, source: str):
        self.source = source
        for scenario in self.scenarios:
            scenario.set_source(source)

    def get_scenario_by_name(self, name: str) -> Optional[Scenario]:
        return next((scenario for scenario in self.scenarios if scenario.name == name), None)

    def validate_feature(self) -> bool:
        """
        Validate the feature to check the following
        If iteration policy is one per iteration, check if the sum of all probability valeus of scenarios is equal to 1
        If iteration policy is some or All per iteration, check if every scenario is valid.
        :return:
        """
        if not self.scenarios:
            return False

        if self.iteration_policy == IterationPolicy.ALL_PER_ITERATION:
            return True
        elif self.iteration_policy == IterationPolicy.SOME_PER_ITERATION:
            return all(scenario.validate_scenario() for scenario in self.scenarios)
        elif self.iteration_policy == IterationPolicy.ONE_PER_ITERATION:
            return round(sum(scenario.probability if scenario.probability else 1.0 for scenario in self.scenarios),
                         2) == 1.0
        else:
            raise NotImplemented(f"Iteration policy {self.iteration_policy} is not implemented.")

    # noinspection PyTypeChecker
    def get_next_iteration_scenarios(self, random: Random) -> list[Scenario]:
        if self.iteration_policy == IterationPolicy.ALL_PER_ITERATION:
            return list(self.scenarios)
        elif self.iteration_policy == IterationPolicy.ONE_PER_ITERATION:
            return [randomization_utils.generate_next_mutex_composition_from_objects(self.scenarios, random)]
        elif self.iteration_policy == IterationPolicy.SOME_PER_ITERATION:
            return randomization_utils.generate_next_composition_from_objects(self.scenarios, random)
        else:
            raise NotImplemented(f"Iteration policy {self.iteration_policy} is not implemented.")
