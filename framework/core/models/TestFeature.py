from typing import Optional

from pydantic import BaseModel

from framework.core.models.TestScenario import TestScenario


class TestFeature(BaseModel):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[list[str]] = []
    background_steps: Optional[list[TestScenario]] = []
    scenarios: list[TestScenario]
