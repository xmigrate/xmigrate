# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient


def create_vm(rg_name, vm_name, location, username, password, vm_type, nic_result, subscription_id, image_name):
    compute_client = get_client_from_cli_profile(ComputeManagementClient)
    print(
        f"Provisioning virtual machine {vm_name}; this operation might take a few minutes.")
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
                                                                          "id": nic_result.id,
                                                                      }]
                                                                  }
                                                              }
                                                              )

    vm_result = poller.result()
    print(f"Provisioned virtual machine {vm_result.name}")
    return True
