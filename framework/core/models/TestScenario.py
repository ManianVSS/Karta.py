from typing import Optional

from pydantic import BaseModel
from framework.core.models.TestStep import TestStep


class TestScenario(BaseModel):
    name: Optional[str]
    steps: Optional[list[TestStep]]
