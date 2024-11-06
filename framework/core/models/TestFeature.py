from typing import Optional

from pydantic import BaseModel

from framework.core.models.TestScenario import TestScenario


class TestFeature(BaseModel):
    name: Optional[str]
    scenarios: Optional[list[TestScenario]]
