from utils.dbconn import *
from model.project import *


def get_project(name, user):
    con = create_db_con()
    if name == "all":
        print(user)
        return Project.objects(users__contains=user).to_json()
    else:
        return Project.objects(name=name, users__contains=user).to_json()


def create_project(provider, location, name, rg, subid, user):
    con = create_db_con()
    users = [user]
    print(users)
    post = Project(name=name, provider=provider, location=location, resource_group=rg, subscription_id=subid, users=users)
    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()


def update_project(provider, location, name, rg, subid, user):
    con = create_db_con()
    try:
        Project.objects(name=name, users__contains=user).update(
            provider=provider, location=location, resource_group=rg, subscription_id=subid)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()
