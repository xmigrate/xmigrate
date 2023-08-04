from .gcp import get_service_compute_v1
from .gcp import REGIONS
from exception.exception import GcpRegionNotFound
from schemas.machines import VMUpdate
from schemas.network import NetworkUpdate, SubnetUpdate
from services.blueprint import get_blueprintid
from services.machines import get_all_machines, update_vm
from services.network import get_all_networks, get_all_subnets, update_network, update_subnet
from services.project import get_project_by_name
from utils.logger import *
import asyncio
import json


# def list_vpc(project_id, service_account_json) -> list[str]:
#     service = get_service_compute_v1(service_account_json)
#     request = service.networks().list(project=project_id)
#     res = []
#     while request is not None:
#         response = request.execute()
#         for network in response['items']:
#             res.append(network)
#         request = service.networks().list_next(
#             previous_request=request, previous_response=response)
#     return res


def get_vpc(service_account_json, network_name):
    service = get_service_compute_v1(service_account_json)
    request = service.networks().get(project=service_account_json["project_id"], network=network_name)
    response = request.execute()
    return response


async def create_vpc(service_account_json, network_name, wait_for_creation=False):
    try:
        print("Provisioning a vpc...some operations might take a minute or two.")
        service = get_service_compute_v1(service_account_json)
        network_body = {
            "name": network_name,
            "autoCreateSubnetworks": False,
        }
        request = service.networks().insert(project=service_account_json["project_id"], body=network_body)
        response = request.execute()
        if wait_for_creation:
            while True:
                result = service.globalOperations().get(project=service_account_json["project_id"], operation=response['name']).execute()
                if result['status'] == 'DONE':
                    print("done.")
                    if 'error' in result:
                        raise Exception(result['error'])
                    return result, True
                await asyncio.sleep(1)
        return response, True
    except Exception as e:
        print(str(e))
        return None, False


# def delete_vpc(project_id, service_account_json, network_name):
#     service = get_service_compute_v1(service_account_json)
#     request = service.networks().delete(project=project_id, network=network_name)
#     return request.execute()


# def list_subnet(project_id, service_account_json, network_name, region):
#     if region not in REGIONS:
#         raise GcpRegionNotFound(region)
#     network = get_vpc(project_id, service_account_json, network_name)
#     service = get_service_compute_v1(service_account_json)
#     request = service.subnetworks().list(project=project_id, region=region)
#     res = []
#     while request is not None:
#         response = request.execute()
#         for subnetwork in response['items']:
#             if network["selfLink"] == subnetwork["network"]:
#                 res.append(subnetwork)
#         request = service.subnetworks().list_next(
#             previous_request=request, previous_response=response)
#     return res


def get_subnet(project_id, service_account_json, subnet_name, region):
    service = get_service_compute_v1(service_account_json)
    request = service.subnetworks().get(project=project_id, region=region, subnetwork=subnet_name)
    response = request.execute()
    return response


def create_subnet(service_account_json, network_name, region, name, cidr):
    try:
        if region not in REGIONS:
            raise GcpRegionNotFound(region)
        service = get_service_compute_v1(service_account_json)
        network = get_vpc(service_account_json, network_name)
        subnetwork_body = {
            "name": name,
            "network": network["selfLink"],
            "ipCidrRange": cidr
        }
        request = service.subnetworks().insert(
            project=service_account_json["project_id"], region=region, body=subnetwork_body)
        response = request.execute()
        return response
    except Exception as e:
        print(str(e))
        return {}


async def create_nw(user, project, db):
    prjct = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(prjct.id, db)
    machines = get_all_machines(blueprint_id, db)
    gcp_service_json = json.loads(prjct.gcp_service_token)

    try:
        for machine in machines:
            networks = get_all_networks(blueprint_id, db)
            for network in networks:
                vpc_id = network.target_network_id
                vpc_created = network.created
                subnets = get_all_subnets(network.id, db)
                update_host = True if network.cidr == machine.network else False
                if vpc_id is None and not vpc_created:
                    response, vpc_created = await create_vpc(gcp_service_json, network.name, True)
                    vpc_id = response['targetLink'] if 'targetLink' in response.keys() else vpc_id
                if vpc_created:
                    network_data = NetworkUpdate(network_id=network.id, target_network_id=vpc_id, created=True)
                    update_network(network_data, db)
                    if update_host:
                        status = 10 if vpc_created else -10
                        vm_data = VMUpdate(machine_id=machine.id, status=status)
                        update_vm(vm_data, db)
                        if status == -10:
                            print("Vnet creation failed to save!")
                            logger("Vnet creation failed to save", "warning")
                            return False
                    for subnet in subnets:
                        if not subnet.created:
                            subnet_result = create_subnet(gcp_service_json, network.name, prjct.location, subnet.subnet_name, subnet.cidr)
                            if 'targetLink' in subnet_result.keys():
                                subnet_data = SubnetUpdate(subnet_id=subnet.id, target_subnet_id=subnet_result['targetLink'], created=True)
                                update_subnet(subnet_data, db)
                            if update_host:
                                status = 20 if 'targetLink' in subnet_result.keys() else -20
                                vm_data = VMUpdate(machine_id=machine.id, status=status)
                                update_vm(vm_data, db)
                                if status == -20:
                                    print("Subnet creation failed to save!")
                                    logger("Subnet creation failed to save", "warning")
        return True
    except Exception as e:
        print(str(e))
        return False
