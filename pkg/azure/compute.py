# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from model.blueprint import Blueprint
from model.disk import Disk
from model.project import Project
from utils.database import dbconn
from utils.logger import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOptionTypes
from sqlalchemy import update


def create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, subscription_id, image_name, project, data_disks, db):
    prjct = db.query(Project).filter(Project.name==project).first()
    client_id = prjct.client_id
    secret = prjct.secret
    tenant_id = prjct.tenant_id
    subscription_id = prjct.subscription_id

    creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
    compute_client = ComputeManagementClient(creds,subscription_id)
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
                                                                          'id': '/subscriptions/' + subscription_id + '/resourceGroups/' + rg_name + '/providers/Microsoft.Compute/images/'+image_name
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
    try:
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
        print("VM creation updation failed: "+repr(e))
        logger("VM creation updation failed: "+repr(e),"warning")


async def create_vm(project, hostname, db):
    prjct = db.query(Project).filter(Project.name==project).first()
    rg_name = prjct.resource_group
    location = prjct.location
    subscription_id = prjct.subscription_id
    username = "xmigrate"
    password = "Xmigrate@321"
    machines = db.query(Blueprint).filter(Blueprint.name==project, Blueprint.host==hostname).all()
    for machine in machines:
        disks =  db.query(Disk).filter(Disk.project==project, Disk.host==machine.host).all()
        data_disks = []
        image_name = ''
        for disk in disks:
            if disk.mnt_path == 'slash':
                image_name = disk.disk_id
            else:
                data_disks.append(disk.disk_id)
        vm_name = machine.host
        vm_type = machine.machine_type
        nic_id = machine.nic_id
        
        create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, subscription_id, image_name, project, data_disks)


def list_available_vm_sizes(compute_client, region = 'EastUS2', minimum_cores = 1, minimum_memory_MB = 768):
    vm_sizes_list = compute_client.virtual_machine_sizes.list(location=region)
    machine_types = []
    for vm_size in vm_sizes_list:
        if vm_size.number_of_cores >= int(minimum_cores) and vm_size.memory_in_mb >= int(minimum_memory_MB): 
            machine_types.append({"vm_name":vm_size.name, "cores":vm_size.number_of_cores, "osdisk":vm_size.os_disk_size_in_mb, "disk":vm_size.resource_disk_size_in_mb, "memory":vm_size.memory_in_mb, "max_data_disk":vm_size.max_data_disk_count})
    return machine_types


def get_vm_types(project, db):
    client = ''
    location = ''
    machine_types = []
    try:
        prjct = db.query(Project).filter(Project.name==project).first()
        subscription_id = prjct.subscription_id
        client_id = prjct.client_id
        tenant_id = prjct.tenant_id
        secret_id = prjct.secret
        location = prjct.location

        creds = ServicePrincipalCredentials(client_id=client_id, secret=secret_id, tenant=tenant_id)
        client = ComputeManagementClient(creds, subscription_id)

        machine_types = list_available_vm_sizes(client, region = location, minimum_cores = 1, minimum_memory_MB = 768)
        flag = True
    except Exception as e:
        print(repr(e))
        logger("Fetching vm details failed: "+repr(e),"warning")
        flag = False
    return machine_types, flag


                
            