from utils.dbconn import *
from model.project import *


def get_project(name):
    con = create_db_con()
    if name == "all":
        return Project.objects.to_json()
    else:
        return Project.objects(name=name).to_json()


def create_project(provider, location, name, rg, subid):
    con = create_db_con()
    post = Project(name=name, provider=provider, location=location, resource_group=rg, subscription_id=subid)
    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()


def update_project(provider, location, name, rg, subid):
    con = create_db_con()
    try:
        Project.objects(name=name).update(
            provider=provider, location=location, resource_group=rg, subscription_id=subid)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()
