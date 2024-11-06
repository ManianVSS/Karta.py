from typing import Optional, Dict

from pydantic import BaseModel


class TestStep(BaseModel):
    name: Optional[str]
    data: Optional[Dict] = None
