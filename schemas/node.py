from pydantic import BaseModel


class NodeCreate(BaseModel):
    project_id: str
    hosts: list
    username: str
    password: str


class NodeUpdate(NodeCreate):
    project_id: None = None
    node_id: str
    hosts: list
    username: str
    password: str


