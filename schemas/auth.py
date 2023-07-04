from pydantic import BaseModel, BaseSettings


class TokenData(BaseModel):
    username: str


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "try2h@ckT415"
    ALGORITHM: str = "HS256"