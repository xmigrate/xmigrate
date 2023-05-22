from model.storage import Storage
from utils.logger import *
from sqlalchemy import update

def get_storage(name, db):
    if name == "all":
        return db.query(Storage).all()
    else:
        return db.query(Storage).filter(Storage.project==name).all()


def create_storage(project, storage, container, access_key, db):
    try:
        strg = Storage(project=project, storage=storage, container=container, access_key=access_key)
        db.add(strg)
        db.commit()
        db.refresh(strg)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False


def update_storage(project, storage, container, access_key, db):
    try:
        db.execute(update(Storage).where(
            Storage.project==project and Storage.storage==storage
            ).values(
            container=container, access_key=access_key
            ).execution_options(synchronize_session="fetch"))
        db.commit()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False