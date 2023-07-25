from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field


class NodeCreate(BaseModel):
    id: str = Field(default_factory=unique_id_gen)
    project: str = Field(alias='project_id')
    hosts: list
    username: str
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


class NodeUpdate(BaseModel):
    id: str = Field(alias='node_id')
    hosts: list
    username: str
    password: str
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True

