# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from utils.dbconn import *
from utils.logger import *
from model.project import Project
import string, random
from azure.common.credentials import ServicePrincipalCredentials

# Provision the resource group.
async def create_rg(project):
    con = create_db_con()
    try:
        if Project.objects(name=project)[0]['resource_group']:
            if Project.objects(name=project)[0]['resource_group_created']:
                return True
    except Exception as e:
        print("Reaching Project document failed: "+repr(e))
        logger("Reaching Project document failed: "+repr(e),"warning")
    else:
        rg_location = Project.objects(name=project)[0]['location']
        rg_name = Project.objects(name=project)[0]['resource_group']
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
            Project.objects(name=project).update(resource_group=rg_result.name, resource_group_created=True)
            con.shutdown()
            return True
        except Exception as e:
            print("Resource group creation failed "+str(e))
            logger("Resource group creation failed: "+repr(e),"warning")
            return False
