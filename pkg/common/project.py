from utils.dbconn import *
from model.project import *
import os, json


def get_project(name, user):
    con = create_db_con()
    print(name)
    if name == "all":
        print(user)
        print([dict(x) for x in Project.objects.all().filter(users__contains=user).allow_filtering()])
        return [dict(x) for x in Project.objects.all().filter(users__contains=user).allow_filtering()]
    else:
        return [ dict(x) for x in Project.objects(name=name, users__contains=user).allow_filtering() ]


async def create_project(data, user):
    con = create_db_con()
    users = [user]
    provider = data.provider
    if provider == 'azure':
        location = data.location
        name = data.name
        resource_group = data.resource_group
        subscription_id = data.subscription_id
        client_id = data.client_id
        secret = data.secret_id
        tenant_id = data.tenant_id
        post = Project(name=name, provider=provider, users=users, location=location, resource_group=resource_group,
                       subscription_id=subscription_id, client_id=client_id, secret=secret, tenant_id=tenant_id)
    elif provider == 'aws':
        aws_dir = os.path.expanduser('~/.aws')
        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)
        name = data.name
        access_key = data.access_key
        secret_key = data.secret_key
        location = data.location
        credentials_str = '['+name+']\naws_access_key_id = ' + \
            access_key+'\n' + 'aws_secret_access_key = '+secret_key
        with open(aws_dir+'/credentials', 'w+') as writer:
            writer.write(credentials_str)
        config_str = '[profile '+name+']\nregion = '+location+'\noutput = json'
        with open(aws_dir+'/config', 'w+') as writer:
            writer.write(config_str)
        post = Project(name=name, provider=provider, users=users,
                       location=location, access_key=access_key, secret_key=secret_key)
    elif provider == 'gcp':
        location = data.location
        name = data.name
        project_id = data.service_account['project_id']
        service_account = data.service_account
        post = Project(name=name, provider=provider, users=users, location=location,
                           service_account=service_account, gcp_project_id=project_id)

    try:
        post.save()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False
    finally:
        con.shutdown()


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
        elif provider == 'gcp':
            location = data['location']
            name = data['name']
            project_id = data['project_id']
            service_account_json = data['service_account']
            Project.objects(name=name, users__contains=user).update(
                location=location, gcp_project_id=project_id, service_account=service_account_json)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(repr(e))
        return False
    finally:
        con.shutdown()
