from pydantic import BaseModel


class MasterUpdate(BaseModel):
    table: str
    host: str
    project: str
    status: int | None = None
    disk_clone: list | None = None
    mountpoint: str | None = None