from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.machines import get_machineid, update_vm
from services.node import get_nodes
from services.project import get_project_by_name
from services.storage import get_storage
from utils.playbook import run_playbook
import json
import os
from sqlalchemy.orm import Session


async def prepare(user: str, project: str, hostname: list, db: Session) -> None:
    project = get_project_by_name(user, project, db)
    node = get_nodes(project.id, db)

    playbook = "xmigrate.yaml"
    stage = "vm_preparation"
    curr_dir = os.getcwd()
    extra_vars = None
    if project.provider == "gcp":
        storage = get_storage(project.id, db)
        extra_vars = {
            'project_id': json.loads(project.gcp_service_token)['project_id'],
            'gs_access_key_id': storage.access_key,
            'gs_secret_access_key': storage.secret_key
        }

    try:
        preparation_completed = run_playbook(project.provider, node.username, project.name, curr_dir, playbook, stage, extra_vars)
    
        if preparation_completed:
            blueprint_id = get_blueprintid(project.id, db)
            machine_id = get_machineid(hostname[0], blueprint_id, db)
            vm_data = VMUpdate(machine_id=machine_id, status=21)
            update_vm(vm_data, db)
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False