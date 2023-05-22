from model.project import Project
from model.storage import GcpBucket
from utils.logger import *
from sqlalchemy import update

def create_bucket(project, bucket, access_key, secret_key, db):
    project_id = (db.query(Project).filter(Project.name==project).first()).gcp_project_id
    try:
        strg = GcpBucket(project=project,bucket=bucket, access_key=access_key,secret_key=secret_key,project_id=project_id)
        db.add(strg)
        db.commit()
        db.refresh(strg)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        logger(str(e),"warning")
        return False

def update_bucket(project, bucket,access_key,secret_key, db):
    project_id = (db.query(Project).filter(Project.name==project).first()).gcp_project_id
    try:
        db.execute(update(GcpBucket).where(
            GcpBucket.project==project and GcpBucket.bucket==bucket
            ).values(
            access_key=access_key, secret_key=secret_key, project_id=project_id
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
        return db.query(GcpBucket).all()
    else:
        return db.query(GcpBucket).filter(GcpBucket.project==name).all()