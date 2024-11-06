from typing import Optional, Dict

from pydantic import BaseModel

from framework.core.models import Constants


class TestStep(BaseModel):
    conjunction: Optional[str] = Constants.THEN
    name: str
    positional_parameters: Optional[list] = []
    data: Optional[Dict] = None
    text: Optional[str] = None
