from typing import List
from numpy import append

from .gcp import get_service_compute_v1


async def list_vpc(project_id, service_account_json) -> List[str]:
    service = get_service_compute_v1(service_account_json)
    request = service.networks().list(project=project_id)
    response = []
    while request is not None:
        response = request.execute()
        for network in response['items']:
            append(response, network)
        request = service.networks().list_next(
            previous_request=request, previous_response=response)
    return response


async def create_vpn(project_id, service_account_json):
    service = get_service_compute_v1(service_account_json)
    network_body = {
        "name": "test-vpc",
        "autoCreateSubnetworks": False,
    }
    request = service.networks().insert(project=project_id, body=network_body)
    response = request.execute()
    return response
