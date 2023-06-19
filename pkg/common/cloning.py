from pkg.azure import sas
from services.blueprint import get_blueprintid
from services.machines import get_machine_by_hostname
from services.node import get_nodes
from services.project import get_project_by_name
from services.storage import get_storage
import json
import os
from ansible_runner import run_async
from sqlalchemy.orm import Session


async def clone(user: str, project: str, hostname: list, db: Session) -> bool:
    project = get_project_by_name(user, project, db)
    storage = get_storage(project.id, db)
    nodes = get_nodes(project.id, db)
    public_ip = ','.join(json.loads(nodes.hosts)['hosts'])
    server = os.getenv('BASE_URL')
    current_dir = os.getcwd()
    os.popen('echo null > ./logs/ansible/migration_log.txt')

    playbook = "{}/ansible/{}/start_migration.yaml".format(current_dir, project.provider)
    inventory = "{}/ansible/projects/{}/hosts".format(current_dir, project.name)
    extravars = None
    
    if project.provider == 'azure':
        sas_token = sas.generate_sas_token(storage.bucket_name, storage.access_key)
        url = f'https://{storage.bucket_name}.blob.core.windows.net/{storage.container}/'
        extravars = {
            'url': url,
            'sas': sas_token,
            'server': server,
            'project': project.name,
            'ansible_user': nodes.username
        }
    elif project.provider in ('aws', 'gcp'):
        extravars = {
        'bucket': storage.bucket_name,
        'access_key': storage.access_key,
        'secret_key': storage.secret_key,
        'server': server,
        'project': project.name,
        'ansible_user': nodes.username
    }
        
    envvars = {
        'ANSIBLE_BECOME_USER': nodes.username,
        'ANSIBLE_LOG_PATH': '{}/logs/ansible/{}/cloning_log.txt'.format(current_dir ,project.name)
    }

    cloned = await run_async(playbook=playbook, inventory=inventory, extravars=extravars, envvars=envvars, limit=public_ip, quiet=True)
    
    if (not (bool(cloned[1].stats['failures']) or bool(cloned[1].stats['dark']))):
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
    else:
        return False