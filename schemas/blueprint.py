from pydantic import BaseModel


class BlueprintCreate(BaseModel):
    project: str
    hostname: str
    machines: list[dict]