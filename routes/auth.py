from schemas.auth import TokenData, Settings
from schemas.user import UserBase
from services.user import check_user_exists, create_user
from utils.database import dbconn
from utils.logger import Logger
from functools import lru_cache
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
import jwt
from sqlalchemy.orm import Session


router = APIRouter()


@lru_cache()
def get_settings() -> Settings:
    return Settings()


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl='login')), settings: Settings = Depends(get_settings)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=jsonable_encoder({'message': 'invalid username or password!'}))


@router.post('/login')
async def login(data: OAuth2PasswordRequestForm = Depends(), settings = Depends(get_settings), db: Session = Depends(dbconn)):
    '''
    Authentication endpoint
    '''

    valid_user = check_user_exists(data.username, db)
    if not valid_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder({"message": "bad username or password!"}))

    token_data = {'username': data.username}
    access_token = jwt.encode(token_data, settings.JWT_SECRET_KEY)
    response_object = {'access_token': access_token}

    return jsonable_encoder(response_object)


@router.post('/signup')
async def signup(data: UserBase, db: Session = Depends(dbconn)):
    try:
        user_exists = check_user_exists(data.username, db)
        if not user_exists:
            return create_user(data.username, data.password, db)
        else:
            return jsonable_encoder({"message": f"user {data.username} already exists!"})
    except Exception as e:
        Logger.info(str(e))
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder({"message": "user creation failed!"}))

@router.get('/user', response_model=TokenData)
async def username(current_user: TokenData = Depends(get_current_user)):
    return jsonable_encoder(current_user)