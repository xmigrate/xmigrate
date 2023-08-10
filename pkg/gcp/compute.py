from .gcp import get_service_compute_v1
from .location import get_zones
from .network import get_vpc
from .network import get_subnet
from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.disk import get_all_disks
from services.machines import get_all_machines, get_machine_by_hostname, update_vm
from services.network import get_all_subnets, get_network_by_cidr
from services.project import get_project_by_name
from utils.logger import Logger
import asyncio
import json


async def create_vm(project, host, network, subnet, additional_disk):
    service_account_json = json.loads(project.gcp_service_token)
    gcp_project_id = service_account_json['project_id']
    service = get_service_compute_v1(service_account_json)
    zones, _ = await get_zones(service_account_json)
    zones = [x for x in zones if project.location in x][::-1]
    vm_type = f"zones/{zones[0]}/machineTypes/{host.machine_type}"
    network = get_vpc(service_account_json, network)['selfLink']
    subnet = get_subnet(gcp_project_id, service_account_json, subnet, project.location)['selfLink']
    
    disks = [
        {
            'boot': True,
            'autoDelete': True,
            "initializeParams": {
                "sourceImage": host.image_id
            }
        }
    ]

    disks.extend(additional_disk)

    instance_body = {
        "name": (host.hostname).replace('.', '-'),
        "machineType": vm_type,
        "disks": disks,
        'networkInterfaces': [{
            'network': network,
            'subnetwork': subnet,
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }]

    }
    request = service.instances().insert(project=gcp_project_id, zone=zones[0], body=instance_body)
    response = request.execute()

    while True:
        result = service.zoneOperations().get(project=gcp_project_id, zone=zones[0], operation=response['name']).execute()
        print(result)

        if result['status'] == 'DONE':
            return result
        
        asyncio.sleep(10)


async def build_compute(user, project, hostname, db):
    try:
        project = get_project_by_name(user, project, db)
        blueprint_id = get_blueprintid(project.id, db)

        if hostname == ["all"]:
            hosts = get_all_machines(blueprint_id, db)
        else:
            hosts = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]

        for host in hosts:
            network = get_network_by_cidr(host.network, blueprint_id, db)
            subnet = ((get_all_subnets(network.id, db)[0]).target_subnet_id).split('v1')[1].split('/')[-1]
            network = (network.target_network_id).split('v1')[1].split('/')[-1]
            disks = get_all_disks(host.id, db)
            extra_disks = []

            for disk in disks:
                if disk.mnt_path in ["slash", "slashboot"]:
                    continue
                else:
                    extra_disks.append(
                        {
                            'boot': True if disk.mnt_path in ["slash", "slashboot"] else False,
                            'autoDelete': True,
                            "source": disk.target_disk_id
                        }
                    )

            if len(extra_disks) > 0:
                Logger.info("Found additional disks")

            try:
                vm_data = VMUpdate(machine_id=host.id, status=95)
                update_vm(vm_data, db)
                vm = await create_vm(project, host, network, subnet, extra_disks)
                
                if 'error' not in vm.keys():
                    Logger.info("vm %s created" %(host.hostname).replace('.', '-'))
                    vm_data = VMUpdate(machine_id=host.id, status=100)
                    update_vm(vm_data, db)
                else:
                    Logger.info("vm %s creation failed" %(host.hostname).replace('.', '-'))
                    vm_data = VMUpdate(machine_id=host.id, status=-100)
                    update_vm(vm_data, db)
                    return False
                ## todo watch vm status
            except Exception as e:
                Logger.info(str(e))
                vm_data = VMUpdate(machine_id=host.id, status=-100)
                update_vm(vm_data, db)
                return False
        return True
    except Exception as e:
        Logger.info(str(e))
        return False