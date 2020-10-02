from utils.dbconn import *
from model.project import *


def get_project(name, user):
    con = create_db_con()
    print(name)
    if name == "all":
        print(user)
        return Project.objects(users__contains=user).to_json()
    else:
        return Project.objects(name=name, users__contains=user).to_json()


async def create_project(data, user):
    con = create_db_con()
    users = [user]
    provider = data['provider']
    if provider == 'azure':
        location = data['location']
        name = data['name']
        resource_group = data['resource_group']
        subscription_id = data['subscription_id']
        client_id = data['client_id']
        secret = data['secret_id']
        tenant_id = data['tenant_id']
        post = Project(name=name, provider=provider, users=users, location=location, resource_group=resource_group, subscription_id=subscription_id, client_id=client_id, secret=secret, tenant_id=tenant_id)
    elif provider == 'aws':
        name = data['name']
        access_key = data['access_key']
        secret_key = data['secret_key']
        location = data['location']
        post = Project(name=name, provider=provider, users=users, location=location, access_key=access_key, secret_key=secret_key)
    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.close()


async def update_project(data, user):
    con = create_db_con()
    provider = data['provider']
    try:
        if provider == 'azure':
            print(user)
            name = data['name']
            location = data['location']
            resource_group = data['resource_group']
            subscription_id = data['subscription_id']
            client_id = data['client_id']
            secret = data['secret_id']
            tenant_id = data['tenant_id']
            Project.objects(name=name, users__contains=user).update(
                location=location, resource_group=resource_group, subscription_id=subscription_id, client_id=client_id, secret=secret, tenant_id=tenant_id)
        elif provider == 'aws':
            name = data['name']
            access_key = data['access_key']
            secret_key = data['secret_key']
            location = data['location']
            Project.objects(name=name, users__contains=user).update(
                location=location, access_key=access_key, secret_key=secret_key)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(repr(e))
        return False
    finally:
        con.close()
