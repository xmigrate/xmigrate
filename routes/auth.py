from pkg.common import user
from utils.database import dbconn
from functools import lru_cache
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
import jwt
from pydantic import BaseModel, BaseSettings
from sqlalchemy.orm import Session
from typing import Union

router = APIRouter()

class UsernamePassword(BaseModel):
    username: Union[str, None] = None
    password: Union[str, None] = None

class TokenData(BaseModel):
    username: str

class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "try2h@ckT415"
    ALGORITHM: str = "HS256"

@lru_cache()
def get_settings():
    return Settings()

async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl='login')), settings = Depends(get_settings)):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid username or password')


@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), settings = Depends(get_settings), db: Session = Depends(dbconn)):
    '''
    Authentication endpoint
    '''
    username = form_data.username
    password = form_data.password

    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder(
            {"msg": "Missing username parameter"}))
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder(
            {"msg": "Missing password parameter"}))

    valid_user = user.check_user(username, password, db)
    if not valid_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder(
            {"msg": "Bad username or password"}))

    token_data = {
        'username': username
    }
    access_token = jwt.encode(token_data, settings.JWT_SECRET_KEY)
    response_object = {
        'access_token': access_token
    }
    return jsonable_encoder(response_object)


@router.post('/signup')
async def signup(username_password: UsernamePassword, db: Session = Depends(dbconn)):
    username = username_password.username
    password = username_password.password
    if not username:
        raise HTTPException(status_code=400, detail=jsonable_encoder(
            {"msg": "Missing username parameter"}))
    if not password:
        raise HTTPException(status_code=400, detail=jsonable_encoder(
            {"msg": "Missing password parameter"}))

    user_added = user.add_user(username, password, db)

    if not user_added:
        return HTTPException(status_code=400, detail=jsonable_encoder({"msg": "User addition failed"}))
    return jsonable_encoder({"msg": "User added successfully"})

@router.get('/user', response_model=TokenData)
async def username(current_user: TokenData = Depends(get_current_user)):
    return jsonable_encoder(current_user)
