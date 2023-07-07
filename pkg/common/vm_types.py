from pkg.gcp.gcp import get_service_compute_v1
from services.project import get_project_by_name
from utils.logger import logger
import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
import boto3
from sqlalchemy.orm import Session


def ec2_instance_types(ec2):
    describe_args = {}
    while True:
        describe_result = ec2.describe_instance_types(**describe_args)
        yield from [i for i in describe_result['InstanceTypes']]
        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']


def list_gcp_vm_types(gcp_service_token, zone):
    service = get_service_compute_v1(gcp_service_token)
    request = service.machineTypes().list(project=gcp_service_token["project_id"], zone=zone)
    machines = []
    machine_types = []

    while request is not None:
        response = request.execute()
        for machine_type in response['items']:
            machines.append(machine_type['name'])
        request = service.machineTypes().list_next(previous_request=request, previous_response=response)

    for machine in machines:
        machine_types.append({'vm_name': machine})

    return machine_types


def list_azure_vm_types(compute_client, region = 'EastUS2', minimum_cores = 1, minimum_memory_MB = 768):
    vm_sizes_list = compute_client.virtual_machine_sizes.list(location=region)
    machine_types = []
    for vm_size in vm_sizes_list:
        if vm_size.number_of_cores >= int(minimum_cores) and vm_size.memory_in_mb >= int(minimum_memory_MB): 
            machine_types.append({"vm_name": vm_size.name, "cores": vm_size.number_of_cores, "osdisk": vm_size.os_disk_size_in_mb, "disk": vm_size.resource_disk_size_in_mb, "memory": vm_size.memory_in_mb, "max_data_disk": vm_size.max_data_disk_count})
    return machine_types


def get_vm_types(user: str, project: str, db: Session):
    prjct = get_project_by_name(user, project, db)
    machine_types = []
    try:
        if prjct.provider == "aws": 
            client = boto3.client('ec2', aws_access_key_id=prjct.aws_access_key, aws_secret_access_key=prjct.aws_secret_key, region_name=prjct.location)
            for ec2_type in ec2_instance_types(client):
                cores = ''
                if 'DefaultCores' in ec2_type['VCpuInfo'].keys():
                    cores = ec2_type['VCpuInfo']['DefaultCores']
                else:
                    cores = str(ec2_type['VCpuInfo']['DefaultVCpus'])+'_vcpus'
                machine_types.append({"vm_name": ec2_type['InstanceType'], "cores": cores, "memory": ec2_type['MemoryInfo']['SizeInMiB']})
        elif prjct.provider == "azure":
            creds = ServicePrincipalCredentials(client_id=prjct.azure_client_id, secret=prjct.azure_client_secret, tenant=prjct.azure_tenant_id)
            client = ComputeManagementClient(creds, prjct.azure_subscription_id)
            machine_types = list_azure_vm_types(client, region=prjct.location, minimum_cores=1, minimum_memory_MB=768)
        elif prjct.provider == "gcp":
            machine_types = list_gcp_vm_types(json.loads(prjct.gcp_service_token), f"{prjct.location}-a")
        flag = True
    except Exception as e:
        print(repr(e))
        logger("Fetching vm details failed: "+repr(e),"warning")
        flag = False
    return machine_types, flag