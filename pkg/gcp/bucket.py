from utils.dbconn import *
from model.storage import *
from utils.logger import *

def create_bucket(project, bucket,access_key,secret_key):
    con = create_db_con()
    post = GcpBucket(project=project,bucket=bucket, access_key=access_key,secret_key=secret_key)
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

def update_bucket(project, bucket,access_key,secret_key):
    con = create_db_con()
    try:
        GcpBucket.objects(project=project).update(
            bucket=bucket,  access_key=access_key,secret_key=secret_key,upsert=True)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.close()