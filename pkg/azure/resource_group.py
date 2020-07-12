# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient


# Provision the resource group.
def create_rg(rg_name, rg_location):
    resource_client = get_client_from_cli_profile(ResourceManagementClient)
    print(f"Provisioning a resource group...some operations might take a minute or two.")
    rg_result = resource_client.resource_groups.create_or_update(
        rg_name, {"location": rg_location})
    print(
        f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")
    return True
