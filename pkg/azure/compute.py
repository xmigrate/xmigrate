from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.disk import get_all_disks
from services.machines import get_all_machines, get_machine_by_hostname, update_vm
from services.project import get_project_by_name
from utils.logger import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOptionTypes


def create_vm_worker(project, machine, username, password, image_name, data_disks, db) -> bool:
    try:
        creds = ServicePrincipalCredentials(client_id=project.azure_client_id, secret=project.azure_client_secret, tenant=project.azure_tenant_id)
        compute_client = ComputeManagementClient(creds, project.azure_subscription_id)
        managed_disks = []

        lun=1
        for disk in data_disks:
            disk_client = compute_client.disks.get(project.azure_resource_group, disk)
            managed_disks.append({
                'lun': lun, 
                'name': disk_client.name,
                'create_option': DiskCreateOptionTypes.attach,
                'managed_disk': {
                    'id': disk_client.id
                }
            })
            lun += 1
            
        print(f"Provisioning virtual machine {machine.hostname}; this operation might take a few minutes...")

        poller = compute_client.virtual_machines.create_or_update(project.azure_resource_group,
                                                                  machine.hostname,
                                                                  {
                                                                    "location": project.location,
                                                                    "storage_profile": {
                                                                        "data_disks": managed_disks,
                                                                        "image_reference": {
                                                                            'id': f'/subscriptions/{project.azure_subscription_id}/resourceGroups/{project.azure_resource_group}/providers/Microsoft.Compute/images/{image_name}'
                                                                        }
                                                                    },
                                                                    "hardware_profile": {
                                                                        "vm_size": machine.machine_type
                                                                    },
                                                                    "os_profile": {
                                                                        "computer_name": machine.hostname,
                                                                        "admin_username": username,
                                                                        "admin_password": password
                                                                    },
                                                                    "network_profile": {
                                                                        "network_interfaces": [{
                                                                            "id": machine.nic_id,
                                                                        }]
                                                                    }
                                                                }
                                                            )

        vm_result = poller.result()
        print(f"Provisioned virtual machine {machine.hostname}.")
        
        vm_data = VMUpdate(machine_id=machine.id, vm_id=vm_result.name, status=100)
        update_vm(vm_data, db)
        return True
    except Exception as e:
        vm_data = VMUpdate(machine_id=machine.id, vm_id=vm_result.name, status=-100)
        update_vm(vm_data, db)

        print("VM creation updation failed: "+ str(e))
        logger("VM creation updation failed: "+ str(e), "warning")
        return False


async def create_vm(user, project, hostname, db) -> bool:
    project = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(project.id, db)

    username = "xmigrate"
    password = "Xmigrate@321"

    if hostname == ["all"]:
        machines = get_all_machines(blueprint_id, db)
    else:
        machines = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]

    for machine in machines:
        disks = get_all_disks(machine.id, db)
        data_disks = []
        image_name = ''
        for disk in disks:
            if disk.mnt_path == 'slash':
                image_name = disk.disk_id
            else:
                data_disks.append(disk.disk_id)
        
        vm_created = create_vm_worker(project, machine, username, password, image_name, data_disks, db)
        if not vm_created: return False
    return True

                
            