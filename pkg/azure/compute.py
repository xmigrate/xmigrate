# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient
from model.project import *
from model.blueprint import *
from utils.dbconn import *



def create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, subscription_id, image_name, project):
    compute_client = get_client_from_cli_profile(ComputeManagementClient)
    print(
        "Provisioning virtual machine {vm_name}; this operation might take a few minutes.")
    print(nic_id)
    poller = compute_client.virtual_machines.create_or_update(rg_name, vm_name,
                                                              {
                                                                  "location": location,
                                                                  "storage_profile": {
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
        con = create_db_con()
        BluePrint.objects(project=project, host=vm_name).update(vm_id=vm_result.name,status=100)
    except Exception as e:
        print("VM creation updation failed: "+repr(e))
    finally:
        con.close()


def create_vm(project):
    con = create_db_con()
    rg_name = Project.objects(name=project)[0]['resource_group']
    location = Project.objects(name=project)[0]['location']
    subscription_id = Project.objects(name=project)[0]['subscription_id']
    username = "xmigrate"
    password = "Xmigrate@13"
    machines = BluePrint.objects(project=project)
    for machine in machines:
        vm_name = machine['host']
        vm_type = machine['machine_type']
        nic_id = machine['nic_id']
        image_name = machine['image_id']
        create_vm_worker(rg_name, vm_name, location, username, password, vm_type, nic_id, subscription_id, image_name, project)
    con.close()