from pkg.aws import location as regions
from pkg.azure import location
from pkg.gcp import location as gcpregions
from schemas.loactions import LocationBase
from utils.constants import Provider
from fastapi import APIRouter,Request
from fastapi.encoders import jsonable_encoder
import json,os
router = APIRouter()

@router.post('/locations')
async def locations_get(data: LocationBase,request: Request):
    provider = data.provider
    test_header = request.headers.get('X-test')
    
    if test_header == "test" :
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_data.json')
        with open(json_file_path, 'r') as json_file:
            test_data = json.load(json_file)
        if provider == 'azure':
            locations = test_data["azure_locations"]
        elif provider == 'aws':
            locations = test_data["aws_locations"]            
        elif provider == 'gcp':
            locations = test_data["gcp_locations"]
        
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
