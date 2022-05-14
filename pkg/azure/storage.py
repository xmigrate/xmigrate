from utils.dbconn import *
from model.storage import *
from utils.logger import *

def get_storage(name):
    con = create_db_con()
    if name == "all":
        return [ dict(x) for x in Storage.objects.allow_filtering() ]
    else:
        return [ dict(x) for x in Storage.objects(project=name).allow_filtering() ]


def create_storage(project, storage, container, access_key):
    con = create_db_con()
    post = Storage(project=project, storage=storage, container=container, access_key=access_key)
    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.shutdown()


def update_storage(project, storage, container, access_key):
    con = create_db_con()
    try:
        Storage.objects(project=project, storage=storage).update(
            container=container, access_key=access_key,upsert=True)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.shutdown()