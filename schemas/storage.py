from utils.id_gen import unique_id_gen
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Union


class StorageCreate(BaseModel):
    id: str = Field(default_factory=unique_id_gen("ST"))
    project: str
    bucket_name: str
    access_key: Union[str, None] = None
    secret_key: Union[str, None] = None
    container: Union[str, None] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StorageUpdate(BaseModel):
    id: Optional[str] = Field(default=None, alias='storage_id')
    project: str
    bucket_name: str
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    container: Optional[str] = None
    updated_at: datetime = Field(datetime.now())

    class Config:
        allow_population_by_field_name = True