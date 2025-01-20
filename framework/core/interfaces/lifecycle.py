import abc
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from framework.core.models.test_catalog import TestFeature, TestScenario, TestStep
from framework.core.models.test_execution import Run, RunResult, FeatureResult, ScenarioResult, StepResult


class DependencyInjector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def register(self, name: str, value: object) -> object:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, *list_of_objects) -> bool:
        raise NotImplementedError


class TestLifecycleHook(metaclass=abc.ABCMeta):
    """
        TestLifecycleHooks are called synchronously in the different phases of test lifecycle
    """

    @abc.abstractmethod
    def run_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def step_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def step_complete(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_complete(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_complete(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def run_complete(self, context: dict):
        raise NotImplementedError


class Event(BaseModel):
    time: Optional[datetime]


class RunStartEvent(Event):
    run: Optional[Run]


class FeatureStartEvent(Event):
    run: Optional[Run] = None
    feature: Optional[TestFeature] = None


class ScenarioStartEvent(Event):
    run: Optional[Run] = None
    feature: Optional[TestFeature] = None
    scenario: Optional[TestScenario] = None


class StepStartEvent(Event):
    run: Optional[Run] = None
    feature: Optional[TestFeature] = None
    scenario: Optional[TestScenario] = None
    step: Optional[TestStep] = None


class StepCompleteEvent(Event):
    run: Optional[Run] = None
    feature: Optional[TestFeature] = None
    scenario: Optional[TestScenario] = None
    step: Optional[TestStep] = None
    result: Optional[StepResult] = None


class ScenarioCompleteEvent(Event):
    run: Optional[Run] = None
    feature: Optional[TestFeature] = None
    scenario: Optional[TestScenario] = None
    result: Optional[ScenarioResult] = None


class FeatureCompleteEvent(Event):
    run: Optional[Run] = None
    feature: Optional[TestFeature] = None
    result: Optional[FeatureResult] = None


class RunCompleteEvent(Event):
    run: Optional[Run] = None
    result: Optional[RunResult] = None


class TestEventListener(metaclass=abc.ABCMeta):
    """
        TestEventListeners are notified of test events asynchronously after occurrence.
        This can be used to create report generators.
    """

    @abc.abstractmethod
    def process_event(self, event: Event):
        raise NotImplementedError
