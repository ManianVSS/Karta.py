from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel


class TestStep(BaseModel):
    conjunction: Optional[str] = None
    name: str
    # positional_parameters: Optional[list] = []
    data: Optional[Dict] = None
    text: Optional[str] = None


class StepResult(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: bool = True
    error: Optional[str] = None
    results: Optional[Dict] = None

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
