from utils.dbconn import *
from model.storage import *
from utils.logger import *

def create_bucket(project, bucket,service_account):
    con = create_db_con()
    post = GcpBucket(project=project,bucket=bucket, service_account=service_account)
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

def update_bucket(project, bucket,service_account):
    con = create_db_con()
    try:
        GcpBucket.objects(project=project).update(
            bucket=bucket, service_account=service_account,upsert=True)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.close()