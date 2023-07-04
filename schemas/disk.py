from pydantic import BaseModel


class DiskCreate(BaseModel):
    hostname: str
    mnt_path: str
    vm_id: str


class DiskUpdate(DiskCreate):
    disk_id: str
    hostname: str | None = None
    mnt_path: str | None = None
    vm_id: str | None = None
    vhd: str | None = None
    file_size: str | None = None
    target_disk_id: str | None = None
    disk_clone: str | None = None

    class Config:
        orm_mode = True