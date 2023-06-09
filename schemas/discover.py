from pydantic import BaseModel
from typing import Union


class DiscoverBase(BaseModel):
    project: str
    provider: str
    hosts: list
    username: str
    password: str