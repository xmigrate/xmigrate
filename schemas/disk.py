from pydantic import BaseModel
from typing import Union


class DiskCreate(BaseModel):
    hostname: str
    mnt_path: str
    machine_id: str


class DiskUpdate(DiskCreate):
    disk_id: str
    vhd: Union[str, None] = None
    file_size: Union[str, None] = None
    disk_clone: Union[str, None] = None

    class Config:
        orm_mode = True