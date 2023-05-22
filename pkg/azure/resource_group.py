# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from model.project import Project
from utils.database import *
from utils.logger import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

# Provision the resource group.
async def create_rg(project, db):
    try:
        if (db.query(Project).filter(Project.name==project).first()).resource_group:
            if (db.query(Project).filter(Project.name==project).first()).resource_group_created:
                return True
    except Exception as e:
        print("Reaching Project document failed: "+repr(e))
        logger("Reaching Project document failed: "+repr(e),"warning")
    else:
        prjct = db.query(Project).filter(Project.name==project).first()
        try:
            creds = ServicePrincipalCredentials(client_id=prjct.client_id, secret=prjct.secret, tenant=prjct.tenant_id)
            resource_client = ResourceManagementClient(creds, prjct.subscription_id)
            print("Provisioning a resource group...some operations might take a minute or two.")
            rg_result = resource_client.resource_groups.create_or_update(
                prjct.resource_group, {"location": prjct.location})
            print(
                "Provisioned resource group "+ rg_result.name+" in the "+rg_result.location+" region")
            Project.objects(name=project).update(resource_group=rg_result.name, resource_group_created=True)
            return True
        except Exception as e:
            print("Resource group creation failed "+str(e))
            logger("Resource group creation failed: "+repr(e),"warning")
            return False
