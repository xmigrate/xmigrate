from model.project import Project
from utils.dbconn import *
from model.storage import *
from utils.logger import *

def create_bucket(project, bucket,access_key,secret_key):
    con = create_db_con()
    project_id = Project.objects(name=project)[0]['gcp_project_id']
    post = GcpBucket(project=project,bucket=bucket, access_key=access_key,secret_key=secret_key,project_id=project_id)
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

def update_bucket(project, bucket,access_key,secret_key):
    con = create_db_con()
    project_id = Project.objects(name=project)[0]['gcp_project_id']
    try:
        GcpBucket.objects(project=project, bucket=bucket).update(
            access_key=access_key,secret_key=secret_key,project_id=project_id)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False
    finally:
        con.shutdown()

def get_storage(name):
    con = create_db_con()
    if name == "all":
        return [dict(x) for x in Storage.objects.allow_filtering()]
    else:
        return [dict(x) for x in Storage.objects(project=name).allow_filtering()]