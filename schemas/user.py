from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    pass
    class Config:
        orm_mode = True