from pydantic import BaseModel
from typing import Optional


class MasterUpdate(BaseModel):
    table: str
    host: str
    project: str
    status: Optional[int] = None
    disk_clone: Optional[list] = None
    mountpoint: Optional[str] = None