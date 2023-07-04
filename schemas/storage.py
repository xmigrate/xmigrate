from pydantic import BaseModel


class StorageBase(BaseModel):
    project: str
    bucket_name: str
    access_key: str | None = None
    secret_key: str | None = None
    container: str | None = None


class StorageCreate(StorageBase):
    class Config:
        orm_mode = True


class StorageUpdate(StorageBase):
    class Config:
        orm_mode = True