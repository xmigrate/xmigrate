from pydantic import BaseModel


class CommonBase(BaseModel):
    project: str


class CommonCreate(CommonBase):
    hostname: list

    class Config:
        orm_mode: True