from pydantic import BaseModel
from typing import List


class BlueprintCreate(BaseModel):
    project: str
    hostname: str
    machines: List[dict]