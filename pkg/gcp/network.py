from typing import List

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


def create_vpc(project_id, service_account_json, network_name):
    service = get_service_compute_v1(service_account_json)
    network_body = {
        "name": network_name,
        "autoCreateSubnetworks": False,
    }
    request = service.networks().insert(project=project_id, body=network_body)
    response = request.execute()
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
    request = service.subnetworks().insert(project=project_id, region=region, body=subnetwork_body)
    response = request.execute()
    return response
