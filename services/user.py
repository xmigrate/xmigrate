from model.user import User
from utils.id_gen import unique_id_gen
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy import Column
from sqlalchemy.orm import Session


def check_user_exists(username: str, db: Session) -> bool:
    '''
    Returns if a user with the given username exists in the current database session.
    
    :param username: username to check
    :param db: active database session
    '''

    return(db.query(User).filter(User.username==username, User.is_deleted==False).count() > 0)


def create_user(username: str, password: str, db: Session) -> JSONResponse:
    '''
    Creates a new user with the given credentials.

    :param username: unique username of the new user
    :param password: password of the new user
    :param db: active database session
    '''
    
    stmt = User(
        id = unique_id_gen(),
        username = username,
        password = password,
        created_at = datetime.now(),
        updated_at = datetime.now()
        )
    
    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "user created", "data": [{}]}, status_code=201)


def get_userid(username: str, db: Session) -> Column[str]:
    '''
    Returns the id of the active user.
    
    :param username: name of the active user
    :param db: active database session
    '''
    
    return(db.query(User).filter(User.username==username, User.is_deleted==False).first().id)