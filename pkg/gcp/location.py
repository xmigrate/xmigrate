from .gcp import get_service_compute_v1
from utils.logger import logger


async def get_regions(service_account_json):
    regions = []
    try:
        service = get_service_compute_v1(service_account_json)
        request = service.regions().list(project=service_account_json['project_id'])

        while request is not None:
            response = request.execute()
            for region in response['items']:
                regions.append(region["name"])

            request = service.regions().list_next(previous_request=request, previous_response=response)
        return regions, True
    except Exception as e:
        print(str(e))
        logger("Fetching available locations failed: "+ str(e), "warning")
        return regions, False


async def get_zones(service_account_json):
    zones = []
    try:
        service = get_service_compute_v1(service_account_json)
        request = service.zones().list(project=service_account_json['project_id'])

        while request is not None:
            response = request.execute()
            for zone in response['items']:
                zones.append(zone['name'])
                
            request = service.zones().list_next(previous_request=request, previous_response=response)
        return zones, True
    except Exception as e:
        print(str(e))
        logger("Fetching available locations failed: "+ str(e), "warning")
        return zones, False