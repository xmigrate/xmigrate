from utils.dbconn import *
from model.storage import *
from utils.logger import *

def create_bucket(project, bucket, secret_key, access_key):
    con = create_db_con()
    post = Bucket(project=project, bucket=bucket, secret_key=secret_key, access_key=access_key)
    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.close()

def update_bucket(project, bucket, secret_key, access_key):
    con = create_db_con()
    try:
        Bucket.objects(project=project).update(
            bucket=bucket, secret_key=secret_key, access_key=access_key,upsert=True)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.close()

def get_storage(name):
    con = create_db_con()
    if name == "all":
        return Storage.objects.to_json()
    else:
        return Storage.objects(project=name).to_json()