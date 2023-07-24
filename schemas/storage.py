from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Union


class StorageBase(BaseModel):
    project: str
    bucket_name: str
    access_key: Union[str, None] = None
    secret_key: Union[str, None] = None
    container: Union[str, None] = None


class StorageCreate(StorageBase):
    class Config:
        orm_mode = True


class StorageUpdate(StorageBase):
    project: str
    bucket_name: str
    id: Optional[str] = Field(default=None, alias='storage_id')
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    container: Optional[str] = None
    updated_at: datetime = Field(datetime.now())

    class Config:
        allow_population_by_field_name = True