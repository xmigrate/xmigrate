from pydantic import BaseModel
from typing import Union


class MasterUpdate(BaseModel):
    table: str
    host: str
    project: str
    status: Union[int, None] = None
    disk_clone: Union[list, None] = None
    mountpoint: Union[str, None] = None