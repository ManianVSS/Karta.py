from typing import Optional

from pydantic import BaseModel

from framework.core.models.TestStep import TestStep


class TestScenario(BaseModel):
    name: str
    description: Optional[str]
    tags: Optional[list[str]] = []
    # setup_steps: Optional[list[TestStep]]
    steps: list[TestStep]
    # teardown_steps: Optional[list[TestStep]]
