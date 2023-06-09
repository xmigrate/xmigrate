from pydantic import BaseModel
from typing import Union


class StorageBase(BaseModel):
    project: str
    bucket: str
    access_key: Union[str, None] = None
    secret_key: Union[str, None] = None
    container: Union[str, None] = None


class StorageCreate(StorageBase):
    pass
    class Config:
        orm_mode = True


class StorageUpdate(StorageBase):
    pass
    class Config:
        orm_mode = True