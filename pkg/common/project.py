from model.project import Project
import os
from sqlalchemy import update


def get_project(name, user, db):
    if name == "all":
        return db.query(Project).filter(Project.users.contains(f"{{{user}}}")).all()
    else:
        return db.query(Project).filter(Project.name==name, Project.users.contains(f"{{{user}}}")).all()


async def create_project(data, user, db):
    users = [user]
    provider = data.provider

    if provider == 'azure':
        prjct = Project(name=data.name, provider=provider, users=users, location=data.location, resource_group=data.resource_group,
                       subscription_id=data.subscription_id, client_id=data.client_id, secret=data.secret_id, tenant_id=data.tenant_id)
    elif provider == 'aws':
        aws_dir = os.path.expanduser('~/.aws')
        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)

        with open(f'{aws_dir}/credentials', 'w+') as cred, open(f'{aws_dir}/config', 'w+') as config:
            cred.write(f'[{data.name}]\naws_access_key_id = {data.access_key}\naws_secret_access_key = {data.secret_key}')
            config.write(f'[profile {data.name}]\nregion = {data.location}\noutput = json')

        prjct = Project(name=data.name, provider=provider, users=users,
                       location=data.location, access_key=data.access_key, secret_key=data.secret_key)
    elif provider == 'gcp':
        prjct = Project(name=data.name, provider=provider, users=users, location=data.location,
                           service_account=data.service_account, gcp_project_id=data.service_account['project_id'])

    try:
        db.add(prjct)
        db.commit()
        db.refresh(prjct)
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(e)
        return False


async def update_project(data, user, db):
    provider = data.provider
    try:
        if provider == 'azure':
            db.execute(update(Project).where(
                Project.name==data.name and Project.users.contains(f"{{{user}}}")
            ).values(
                location=data.location, resource_group=data.resource_group, subscription_id=data.subscription_id, client_id=data.client_id, secret=data.secret, tenant_id=data.tenant_id
            ).execution_options(synchronize_session="fetch"))
            db.commit()
        elif provider == 'aws':
            db.execute(update(Project).where(
                Project.name==data.name and Project.users.contains(f"{{{user}}}")
            ).values(
                location=data.location, access_key=data.access_key, secret_key=data.secret_key
            ).execution_options(synchronize_session="fetch"))
            db.commit()
        elif provider == 'gcp':
            db.execute(update(Project).where(
                Project.name==data.name and Project.users.contains(f"{{{user}}}")
            ).values(
                location=data.location, gcp_project_id=data.project_id, service_account=data.service_account
            ).execution_options(synchronize_session="fetch"))
            db.commit()
        return True
    except Exception as e:
        print("Boss you have to see this!!")
        print(repr(e))
        return False