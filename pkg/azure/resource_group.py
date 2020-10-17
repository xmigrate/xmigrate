# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from utils.dbconn import *
from model.project import Project
import string, random
from azure.common.credentials import ServicePrincipalCredentials

# Provision the resource group.
def create_rg(project):
    con = create_db_con()
    try:
        if Project.objects(name=project)[0]['resource_group']:
            return True
    except Exception as e:
        print("Reaching Project document failed: "+repr(e))
    else:
        rg_location = Project.objects(name=project)[0]['location']
        rg_name =''.join(random.choices(string.ascii_uppercase +
                                string.digits, k = 8))
        rg_name = rg_name + "_xmigrate" 
        try:
            client_id = Project.objects(name=project)[0]['client_id']
            secret = Project.objects(name=project)[0]['secret']
            tenant_id = Project.objects(name=project)[0]['tenant_id']
            subscription_id = Project.objects(name=project)[0]['subscription_id']
            creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
            resource_client = ResourceManagementClient(creds,subscription_id)
            print("Provisioning a resource group...some operations might take a minute or two.")
            rg_result = resource_client.resource_groups.create_or_update(
                rg_name, {"location": rg_location})
            print(
                "Provisioned resource group"+ rg_result.name+" in the "+rg_result.location+" region")
            Project.objects(name=project).update(resource_group=rg_result.name)
            con.close()
            return True
        except Exception as e:
            print("Resource group creation failed "+str(e))
            return False
