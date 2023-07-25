from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class DiskCreate(BaseModel):
    id: str = Field(default=unique_id_gen("DK"))
    hostname: str
    mnt_path: str
    vm: str = Field(alias='vm_id')
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


class DiskUpdate(BaseModel):
    id: str = Field(alias='disk_id')
    hostname: Optional[str] = None
    mnt_path: Optional[str] = None
    vm: Optional[str] = Field(default=None, alias='vm_id')
    vhd: Optional[str] = None
    file_size: Optional[str] = None
    target_disk_id: Optional[str] = None
    disk_clone: Optional[list] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True