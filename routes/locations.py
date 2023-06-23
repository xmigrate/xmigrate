from pkg.aws import location as regions
from pkg.azure import location
from pkg.gcp import location as gcpregions
from schemas.loactions import LocationBase
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post('/locations')
async def locations_get(data: LocationBase):
    provider = data.provider
    if provider == 'azure':
        locations, flag = location.get_locations(data.azure_subscription_id, data.azure_client_id, data.azure_client_secret, data.azure_tenant_id)

        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
        
    elif provider == 'aws':
        locations, flag = regions.get_locations(data.aws_access_key, data.aws_secret_key)

        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
        
    elif provider == 'gcp':
        service_account = data.gcp_service_token

        reg, flag = gcpregions.get_regions(service_account)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': reg})
        else:
            return jsonable_encoder({'status': '500', 'locations': reg, 'message':"wrong credentials"})
