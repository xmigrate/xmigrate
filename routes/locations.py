from pkg.aws import location as regions
from pkg.azure import location
from pkg.gcp import location as gcpregions
from schemas.locations import LocationBase
from pkg.test_header_files.test_data import location_test_data
from utils.constants import Provider, Test
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
router = APIRouter()

@router.post('/locations')
async def locations_get(data: LocationBase, request: Request):
    test_header = request.headers.get(Test.HEADER.value)
    
    if test_header is not None:
        locations = await location_test_data(data.provider)
        return jsonable_encoder({'status': '200', 'locations': locations})
    
    if data.provider == Provider.AZURE.value:
        locations, flag = await location.get_locations(data.azure_subscription_id, data.azure_client_id, data.azure_client_secret, data.azure_tenant_id)

        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
        
    elif data.provider == Provider.AWS.value:
        locations, flag = await regions.get_locations(data.aws_access_key, data.aws_secret_key)

        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
        
    elif data.provider == Provider.GCP.value:
        reg, flag = await gcpregions.get_regions(data.gcp_service_token)
        
        if flag:
            return jsonable_encoder({'status': '200', 'locations': reg})
        else:
            return jsonable_encoder({'status': '500', 'locations': reg, 'message':"wrong credentials"})
