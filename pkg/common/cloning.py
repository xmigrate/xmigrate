from pkg.azure import sas
from schemas.auth import Settings
from services.blueprint import get_blueprintid
from services.machines import get_machine_by_hostname
from services.node import get_nodes
from services.project import get_project_by_name
from services.storage import get_storage
from utils.constants import Provider
from utils.playbook import run_playbook
import asyncio
import json
import os
import jwt
from sqlalchemy.orm import Session


async def clone(user: str, project: str, hostname: list, db: Session, settings: Settings = Settings()) -> bool:
    project = get_project_by_name(user, project, db)
    storage = get_storage(project.id, db)
    nodes = get_nodes(project.id, db)
    public_ip = ','.join(json.loads(nodes.hosts))

    # Because all endpoints are authenticated, without this token the payloads can't make successfull api calls.
    token_data = {'username': user}
    access_token = jwt.encode(token_data, settings.JWT_SECRET_KEY)

    server = os.getenv('BASE_URL')
    current_dir = os.getcwd()

    STAGE = "cloning"
    PLAYBOOK = "start_migration.yaml"
    extravars = None
    
    if project.provider == Provider.AZURE.value:
        sas_token = sas.generate_sas_token(storage.bucket_name, storage.access_key)
        url = f'https://{storage.bucket_name}.blob.core.windows.net/{storage.container}/'
        extravars = {
            'url': url,
            'sas': sas_token,
            'server': server,
            'project': project.name,
            'hostname': hostname[0],
            'token': access_token.decode(),
            'ansible_user': nodes.username
        }
    elif project.provider in (Provider.AWS.value, Provider.GCP.value):
        extravars = {
            'bucket': storage.bucket_name,
            'access_key': storage.access_key,
            'secret_key': storage.secret_key,
            'server': server,
            'project': project.name,
            'hostname': hostname[0],
            'token': access_token.decode(),
            'ansible_user': nodes.username
        }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_playbook, project.provider, nodes.username, project.name, current_dir, PLAYBOOK, STAGE, extravars, public_ip)
    except Exception as e:
        raise RuntimeError(f"Error occured while trying to run the playbook: {str(e)}")
    else:
        blueprint_id = get_blueprintid(project.id, db)
        machines = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]
        machine_count = len(machines)
        flag = True
        status_count = 0
        while flag:
            for machine in machines:
                if machine.status >= 25:
                    status_count += 1
            if status_count == machine_count:
                flag = False
        return not flag