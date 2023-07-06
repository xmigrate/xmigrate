from pydantic import BaseModel
from typing import Union


class NodeCreate(BaseModel):
    project_id: str
    hosts: list
    username: str
    password: str


class NodeUpdate(NodeCreate):
    project_id: Union[str, None] = None
    node_id: str
    hosts: list
    username: str
    password: str


