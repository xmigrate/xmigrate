from schemas.blueprint import BlueprintCreate
from schemas.discover import DiscoverCreate, DiscoverUpdate
from schemas.disk import DiskCreate, DiskUpdate
from schemas.machines import VMCreate, VMUpdate
from schemas.network import NetworkCreate, SubnetCreate
from schemas.project import ProjectCreate
from services.blueprint import check_blueprint_exists, create_blueprint, get_blueprintid
from services.discover import check_discover_exists, create_discover, get_discoverid, update_discover
from services.disk import check_disk_exists, create_disk, get_diskid,update_disk
from services.machines import check_vm_exists, create_vm, get_all_machines, get_machineid, update_vm
from services.network import check_network_exists, check_subnet_exists, create_network, create_subnet, get_all_networks
from services.project import check_project_exists, get_project_by_name
from utils.constants import Provider
import json, os
from sqlalchemy.orm import Session


async def get_test_data()-> dict:
    '''Return test data json.'''

    base_dir = os.getcwd()
    with open(f'{base_dir}/pkg/test_header_files/test_data.json', 'r') as json_file:
        test_data = json.load(json_file)

    return test_data


async def project_test_data(user: str, data: ProjectCreate, db: Session) -> ProjectCreate:
    '''Return project test data.'''

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
    '''Return location test data.'''

    test_data = await get_test_data()

    if provider == Provider.AZURE.value:
        locations = test_data["azure_locations"]
    elif provider == Provider.AWS.value:
        locations = test_data["aws_locations"]
    elif provider == Provider.GCP.value:
        locations = test_data["gcp_locations"]

    return locations


async def discover_test_data(project: str, project_id: str, db: Session) -> None:
    '''Simulate discover with test data.'''
    
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


async def migration_test_data(user: str, project: str, status: int, db: Session, hostname: list = None) -> None:
    '''Simlates the process and updates database for build stages.'''

    project = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(project.id, db)
    if hostname is None:
        machines = get_all_machines(blueprint_id, db)
        for machine in machines:
            vm_data = VMUpdate(machine_id=machine.id,status=status)
            update_vm(vm_data, db)
    else:
        machine_id = get_machineid(hostname[0], blueprint_id, db)
        vm_data = VMUpdate(machine_id=machine_id,status=status)
        update_vm(vm_data, db)


async def blueprint_save_test_data(provider: str, blueprint_id: str, data: BlueprintCreate, db: Session):
    '''Save blueprint with test data.'''

    test_data = await get_test_data()
    for machine in data.machines:
        machine_id = get_machineid(machine["hostname"], blueprint_id, db)
        vm_data = VMUpdate(machine_id=machine_id, machine_type=test_data[f"{provider}_machine_types"][0], public_route=bool(test_data["public_route"]))
        update_vm(vm_data, db)


async def network_create_test_data(data: NetworkCreate, db: Session) -> None:
    '''Save network with test data.'''

    test_data = await get_test_data()

    data.cidr = test_data["network_data"]["cidr"] if data.cidr is None else data.cidr
    data.name = test_data["network_data"]["name"] if data.name is None else data.name
    
    network_exists = check_network_exists(data.blueprint, data.cidr, data.name, db)
    if not network_exists:
        create_network(data, db)
    else:
        print(f'Network with cidr ({data.cidr}) and/or name ({data.name}) already exists for the project!')

    for host in data.hosts:
        networks = get_all_networks(data.blueprint, db)
        machine_id = get_machineid(host['hostname'], data.blueprint, db)
        vm_data = VMUpdate(machine_id=machine_id, network=networks[0].cidr)
        update_vm(vm_data, db)


async def subnet_create_test_data(data: SubnetCreate, db) -> None:
    '''Save subnet with test data.'''

    test_data = await get_test_data()

    data.cidr = test_data["subnet_data"]["cidr"] if data.cidr is None else data.cidr
    data.subnet_name = test_data["subnet_data"]["name"] if data.subnet_name is None else data.subnet_name

    subnet_exists = check_subnet_exists(data.network, data.cidr, data.subnet_name, db)
    if not subnet_exists:
        return create_subnet(data, db)
    else:
        print(f'Subnet with cidr ({data.cidr}) and/or name ({data.subnet_name}) already exists for the network {data.nw_cidr}!')
