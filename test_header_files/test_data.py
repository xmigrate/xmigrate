from schemas.project import ProjectBase
from services.project import check_project_exists
from utils.constants import Provider
import json, os
from sqlalchemy.orm import Session

from schemas.discover import DiscoverBase, DiscoverCreate, DiscoverUpdate
from schemas.disk import DiskCreate, DiskUpdate
from schemas.machines import VMCreate, VMUpdate
from schemas.node import NodeCreate, NodeUpdate
from services.blueprint import check_blueprint_exists, create_blueprint, get_blueprintid
from services.discover import check_discover_exists, create_discover, get_discoverid, update_discover
from services.disk import check_disk_exists, create_disk, get_diskid,update_disk
from services.machines import check_vm_exists, create_vm, get_machineid, update_vm
from services.node import check_node_exists, create_node, get_nodeid, update_node
from services.project import get_projectid, get_project_by_name


async def get_test_data()-> dict:
    with open('./test_data.json', 'r') as json_file:
        test_data = json.load(json_file)

    return test_data


async def project_test_data(user: str, data: ProjectBase, db: Session) -> ProjectBase:
    test_data = await get_test_data()

    project_exists = check_project_exists(user, data.name, db)
    if not project_exists:
        if data.provider == Provider.AWS.value:
            if data.aws_access_key is None:
                data.aws_access_key = test_data["aws_access_key"]
            if data.aws_secret_key is None:
                data.aws_secret_key = test_data["aws_secret_key"]
        
        if data.provider == Provider.AZURE.value:
            if data.azure_client_id is None:
                data.azure_client_id = test_data["azure_client_id"]
            if data.azure_client_secret is None:
                data.azure_client_secret = test_data["azure_client_secret"]
            if data.azure_tenant_id is None:
                data.azure_tenant_id = test_data["azure_tenant_id"]
            if data.azure_subscription_id is None:
                data.azure_subscription_id = test_data["azure_subscription_id"]
            if data.azure_resource_group is None:
                data.azure_resource_group = test_data["azure_resource_group"]
            if data.azure_resource_group_created is None:
                data.azure_resource_group_created = test_data["azure_resource_group_created"]

        if data.provider == Provider.GCP.value:
            if data.gcp_service_token is None:
                data.gcp_service_token = test_data["gcp_service_token"]

    return data


async def location_test_data(provider: str) -> list:
    test_data = await get_test_data()

    if provider == Provider.AZURE.value:
        locations = test_data["azure_locations"]
    elif provider == Provider.AWS.value:
        locations = test_data["aws_locations"]
    elif provider == Provider.GCP.value:
        locations = test_data["gcp_locations"]

    return locations


async def discover_test_data(project: str, project_id: str, db: Session) -> None:
    log_file_dir = f"./logs/ansible/{project}"

    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)

    with open(f"{log_file_dir}/gather_facts_log.txt", "w") as log_file:
        log_file.write("PLAY RECAP unreachable=0 failed=0")

    test_data = await get_test_data()
    
    discover_exists = check_discover_exists(project_id, db)
    if not discover_exists:
        discover_data = DiscoverCreate(project_id=project_id, hostname=test_data["host"], network=test_data["network"], subnet=test_data["subnet"], cpu_core=test_data["cores"], cpu_model=test_data["cpu_model"], ram=test_data["ram"], disk_details=test_data["disk"], ip=test_data["ip"])
        create_discover(discover_data, db)
    else:
        discover_id = get_discoverid(project_id, db)
        discover_data = DiscoverUpdate(discover_id=discover_id, hostname=test_data["host"], network=test_data["network"], subnet=test_data["subnet"], cpu_core=test_data["cores"], cpu_model=test_data["cpu_model"], ram=test_data["ram"], disk_details=test_data["disk"], ip=test_data["ip"])
        update_discover(discover_data, db)
    
    blueprint_exists = check_blueprint_exists(project_id, db)
    if not blueprint_exists:
        create_blueprint(project_id, db)

    blueprint_id = get_blueprintid(project_id, db)         
    vm_exists = check_vm_exists(test_data["host"], blueprint_id, db)
    if not vm_exists:
        vm_data = VMCreate(blueprint_id=blueprint_id, hostname=test_data["host"], network=test_data["network"],  cpu_core=test_data["cores"], cpu_model=test_data["cpu_model"], ram=test_data["ram"])
        create_vm(vm_data, db)
    else:
        machine_id = get_machineid(test_data["host"], blueprint_id, db)
        vm_data = VMUpdate(machine_id=machine_id, network=test_data["network"],  cpu_core=test_data["cores"], cpu_model=test_data["cpu_model"], ram=test_data["ram"])
        update_vm(vm_data, db)
    
    disks=test_data["disk"]
    machine_id = get_machineid(test_data["host"], blueprint_id, db)
    for disk in disks:
        mnt_path = disk['mnt_path'].replace('/', 'slash')
        disk_exists = check_disk_exists(machine_id, mnt_path, db)
        if not disk_exists:
            disk_data = DiskCreate(hostname=test_data["host"], mnt_path=mnt_path, vm_id=machine_id)
            create_disk(disk_data, db)
        else:
            disk_id = get_diskid(machine_id, mnt_path, db)
            disk_data = DiskUpdate(disk_id=disk_id, hostname=test_data["host"], mnt_path=mnt_path, vm_id=machine_id)
            update_disk(disk_data, db)


async def migration_test_data(user: str, project: str, hostname: list, status: int, db: Session) -> None:
    project = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(project.id, db)
    machine_id = get_machineid(hostname[0], blueprint_id, db)
    vm_data = VMUpdate(machine_id=machine_id,status=status)
    update_vm(vm_data, db)