from model.user import User
from utils.database import dbconn
from fastapi import Depends
from sqlalchemy.orm import Session

def add_user(username, password, db: Session):
    try:
        data = User(username = username, password = password)
        db.add(data)
        db.commit()
        db.refresh(data)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False

def check_user(username, password, db: Session):
    try:
        if db.query(User).filter(User.username==username, User.password==password).count() == 1:
            return True
        else:
            return False
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False