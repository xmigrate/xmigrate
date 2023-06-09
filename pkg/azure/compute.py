# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from model.blueprint import Blueprint
from model.disk import Disk
from model.project import Project
from utils.logger import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOptionTypes
from sqlalchemy import update


def create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, image_name, project, data_disks, db):
    try:
        prjct = db.query(Project).filter(Project.name==project).first()

        creds = ServicePrincipalCredentials(client_id=prjct.client_id, secret=prjct.secret, tenant=prjct.tenant_id)
        compute_client = ComputeManagementClient(creds, prjct.subscription_id)
        managed_disks = []

        lun=1
        for disk in data_disks:
            disk_client = compute_client.disks.get(rg_name, disk)
            managed_disks.append({
                'lun': lun, 
                'name': disk_client.name,
                'create_option': DiskCreateOptionTypes.attach,
                'managed_disk': {
                    'id': disk_client.id
                }
            })
            lun = lun + 1
            
        
        print(f"Provisioning virtual machine {vm_name}; this operation might take a few minutes.")

        poller = compute_client.virtual_machines.create_or_update(rg_name, vm_name,
                                                                {
                                                                    "location": location,
                                                                    "storage_profile": {
                                                                        "data_disks": managed_disks,
                                                                        "image_reference": {
                                                                            'id': f'/subscriptions/{prjct.subscription_id}/resourceGroups/{rg_name}/providers/Microsoft.Compute/images/{image_name}'
                                                                        }
                                                                    },
                                                                    "hardware_profile": {
                                                                        "vm_size": vm_type
                                                                    },
                                                                    "os_profile": {
                                                                        "computer_name": vm_name,
                                                                        "admin_username": username,
                                                                        "admin_password": password
                                                                    },
                                                                    "network_profile": {
                                                                        "network_interfaces": [{
                                                                            "id": nic_id,
                                                                        }]
                                                                    }
                                                                }
                                                                )

        vm_result = poller.result()
        print("Provisioned virtual machine")
        
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==vm_name
            ).values(
            vm_id=vm_result.name, status='100'
            ).execution_options(synchronize_session="fetch"))
        db.commit()
    except Exception as e:
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==vm_name
            ).values(
            vm_id=vm_result.name, status='-100'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        print("VM creation updation failed: "+ repr(e))
        logger("VM creation updation failed: "+ repr(e),"warning")


async def create_vm(project, hostname, db):
    prjct = db.query(Project).filter(Project.name==project).first()

    username = "xmigrate"
    password = "Xmigrate@321"

    machines = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==hostname).all()

    for machine in machines:
        disks =  db.query(Disk).filter(Disk.project==project, Disk.host==machine.host).all()
        data_disks = []
        image_name = ''
        for disk in disks:
            if disk.mnt_path == 'slash':
                image_name = disk.disk_id
            else:
                data_disks.append(disk.disk_id)
        
        create_vm_worker(prjct.resource_group, machine.host, prjct.location, username, password, machine.machine_type, machine.nic_id, image_name, project, data_disks, db)


                
            