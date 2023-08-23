from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.machines import get_machineid, update_vm
from services.node import get_nodes
from services.project import get_project_by_name
from services.storage import get_storage
from utils.constants import Provider
from utils.logger import Logger
from utils.playbook import run_playbook
import asyncio
import json
import os
from sqlalchemy.orm import Session


async def prepare(user: str, project: str, hostname: list, db: Session) -> None:
    project = get_project_by_name(user, project, db)
    node = get_nodes(project.id, db)

    PLAYBOOK = "xmigrate.yaml"
    STAGE = "vm_preparation"
    current_dir = os.getcwd()
    extra_vars = None
    if project.provider == Provider.GCP.value:
        storage = get_storage(project.id, db)
        extra_vars = {
            'project_id': json.loads(project.gcp_service_token)['project_id'],
            'gs_access_key_id': storage.access_key,
            'gs_secret_access_key': storage.secret_key
        }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_playbook, project.provider, node.username, project.name, current_dir, PLAYBOOK, STAGE, extra_vars)
    
        blueprint_id = get_blueprintid(project.id, db)
        machine_id = get_machineid(hostname[0], blueprint_id, db)
        vm_data = VMUpdate(machine_id=machine_id, status=21)
        update_vm(vm_data, db)
        return True
    except Exception as e:
        Logger.error(str(e))
        return False