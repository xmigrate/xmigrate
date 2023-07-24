from datetime import datetime
from pydantic import BaseModel, Field


class NodeCreate(BaseModel):
    project_id: str
    hosts: list
    username: str
    password: str


class NodeUpdate(BaseModel):
    id: str = Field(alias='node_id')
    hosts: list
    username: str
    password: str
    updated_at: datetime = Field(default_factory=datetime.now())

    class Config:
        allow_population_by_field_name = True

