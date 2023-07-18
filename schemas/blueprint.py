from pydantic import BaseModel
from typing import List


class BlueprintCreate(BaseModel):
    project: str
    machines: List[dict]