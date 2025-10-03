from typing import Optional

from pydantic import BaseModel

from karta.core.models.test_catalog import TestFeature, TestStep, TestScenario


class RunInfo(BaseModel):
    name: Optional[str] = "Karta Run"
    description: Optional[str] = "Run description"
    context: Optional[dict] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TagRunInfo(RunInfo):
    tags: list[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FeatureRunInfo(RunInfo):
    feature: TestFeature

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FeatureSourceRunInfo(RunInfo):
    source: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ScenarioRunInfo(RunInfo):
    scenario: TestScenario
    feature_name: Optional[str] = None
    iteration_index: Optional[int] = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StepRunInfo(RunInfo):
    step: TestStep
    feature_name: Optional[str] = None
    iteration_index: Optional[int] = 0
    scenario_name: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
