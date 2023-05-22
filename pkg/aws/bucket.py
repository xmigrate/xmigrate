from model.storage import Bucket
from utils.logger import *
from sqlalchemy import update

def create_bucket(project, bucket, secret_key, access_key, db):
    try:
        strg = Bucket(project=project, bucket=bucket, secret_key=secret_key, access_key=access_key)
        db.add(strg)
        db.commit()
        db.refresh(strg)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False

def update_bucket(project, bucket, secret_key, access_key, db):
    try:
        db.execute(update(Bucket).where(
            Bucket.project==project and Bucket.bucket==bucket
            ).values(
            secret_key=secret_key, access_key=access_key
            ).execution_options(synchronize_session="fetch"))
        db.commit()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False

def get_storage(name, db):
    if name == "all":
        return db.query(Bucket).all()
    else:
        return db.query(Bucket).filter(Bucket.project==name).all()