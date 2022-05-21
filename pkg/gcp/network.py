from typing import List
from mongoengine import *
from model.blueprint import *
from model.project import *
from model.network import *
from utils.dbconn import *
from utils.logger import *
import asyncio
from exception.exception import GcpRegionNotFound

from .gcp import get_service_compute_v1
from .gcp import REGIONS


def list_vpc(project_id, service_account_json) -> List[str]:
    service = get_service_compute_v1(service_account_json)
    request = service.networks().list(project=project_id)
    res = []
    while request is not None:
        response = request.execute()
        for network in response['items']:
            res.append(network)
        request = service.networks().list_next(
            previous_request=request, previous_response=response)
    return res


def get_vpc(project_id, service_account_json, network_name):
    service = get_service_compute_v1(service_account_json)
    request = service.networks().get(project=project_id, network=network_name)
    response = request.execute()
    return response


async def create_vpc(project_id, service_account_json, network_name, wait_for_creation=False):
    service = get_service_compute_v1(service_account_json)
    network_body = {
        "name": network_name,
        "autoCreateSubnetworks": False,
    }
    request = service.networks().insert(project=project_id, body=network_body)
    response = request.execute()
    if wait_for_creation:
        while True:
            result = service.globalOperations().get(project=project_id, operation=response['name']).execute()
            if result['status'] == 'DONE':
                print("done.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result
            await asyncio.sleep(1)
    return response


def delete_vpc(project_id, service_account_json, network_name):
    service = get_service_compute_v1(service_account_json)
    request = service.networks().delete(project=project_id, network=network_name)
    return request.execute()


def list_subnet(project_id, service_account_json, network_name, region):
    if region not in REGIONS:
        raise GcpRegionNotFound(region)
    network = get_vpc(project_id, service_account_json, network_name)
    service = get_service_compute_v1(service_account_json)
    request = service.subnetworks().list(project=project_id, region=region)
    res = []
    while request is not None:
        response = request.execute()
        for subnetwork in response['items']:
            if network["selfLink"] == subnetwork["network"]:
                res.append(subnetwork)
        request = service.subnetworks().list_next(
            previous_request=request, previous_response=response)
    return res


def get_subnet(project_id, service_account_json, subnet_name, region):
    service = get_service_compute_v1(service_account_json)
    request = service.subnetworks().get(project=project_id, region=region, subnetwork=subnet_name)
    response = request.execute()
    return response


def create_subnet(project_id, service_account_json, network_name, region, name, cidr):
    if region not in REGIONS:
        raise GcpRegionNotFound(region)
    service = get_service_compute_v1(service_account_json)
    network = get_vpc(project_id, service_account_json, network_name)
    subnetwork_body = {
        "name": name,
        "network": network["selfLink"],
        "ipCidrRange": cidr
    }
    request = service.subnetworks().insert(
        project=project_id, region=region, body=subnetwork_body)
    response = request.execute()
    return response


async def create_nw(project):

    con = create_db_con()
    location = Project.objects(name=project).allow_filtering()[0]['location']
    project_id = Project.objects(name=project).allow_filtering()[0]['gcp_project_id']
    service_account_json = Project.objects(name=project).allow_filtering()[0]['service_account']

    machines = BluePrint.objects(project=project).allow_filtering()

    vpc = []
    subnet = []
    for machine in machines:
        vpc.append(machine['network'])
        subnet.append(machine['subnet'])

    vpc = list(set(vpc))
    vpc_created = []
    
    for network_name in vpc:
        print("Provisioning a vpc...some operations might take a minute or two.")
        con = create_db_con()
        created = Network.objects(nw_name=network_name, project=project).allow_filtering()[0]['created']
        if not created:
            try:
                res = await create_vpc(project_id, service_account_json, network_name, True)
                hosts = [x['host'] for x in BluePrint.objects(network=network_name, project=project).allow_filtering()]
                for host in hosts:
                    try:
                        BluePrint.objects(host=host, project=project).update(vpc_id=res['targetLink'], status='10')
                    except Exception as e:
                        BluePrint.objects(host=host, project=project).update(vpc_id=res, status='-10')
                Network.objects(nw_name=network_name, project=project).update(created=True)
            except Exception as e:
                print("Vnet creation failed to save: "+repr(e))
                logger("Vnet creation failed to save: "+repr(e), "warning")
                vpc_created.append(False)
            finally:
                con.shutdown()
            vpc_created.append(True)
        else:
            vpc_created.append(True)
    c = 0
    if False in vpc_created:
        return False
    else:
        subnet = list(set(subnet))
        subnet_created = []
        for i in subnet:
            print("Provisioning a subnet...some operations might take a minute or two.")
            con = create_db_con()
            created = Subnet.objects(cidr=i, project=project).allow_filtering()[0]['created']
            if not created:
                try:
                    subnet_name = project+"subnet"+str(c)
                    subnet_result = create_subnet(project_id, service_account_json,network_name, location, subnet_name, i)
                    hosts = [x['host'] for x in BluePrint.objects(subnet=i,project=project).allow_filtering()]
                    for host in hosts:
                        try:
                            BluePrint.objects(host=host,project=project).update(subnet_id=str(subnet_result['targetLink']),status='20')
                        except Exception as e:
                            BluePrint.objects(host=host,project=project).update(subnet_id=str(subnet_result['targetLink']),status='-20')
                    subnet_name = Subnet.objects(cidr=i, project=project).allow_filtering()[0]['subnet_name']
                    Subnet.objects(cidr=i, project=project, subnet_name=subnet_name).update(created=True)
                except Exception as e:
                    print("Subnet creation failed to save: "+repr(e))
                    logger("Subnet creation failed to save: "+repr(e), "warning")
                    subnet_created.append(False) 
                finally:
                    con.shutdown()
                subnet_created.append(True) 
            else:
                subnet_created.append(True) 
        if False in subnet_created:
            return False      
    con.shutdown()
    return True
