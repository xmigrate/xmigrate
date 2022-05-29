from app import app
import os
import json
from quart import jsonify, request
from pkg.azure import location
from pkg.aws import location as regions
from pkg.gcp import location as gcpregions
from quart_jwt_extended import jwt_required, get_jwt_identity
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from routes.auth import TokenData, get_current_user


@app.post('/locations')
async def locations_get(provider: str, current_user: TokenData = Depends(get_current_user)):
    if provider == 'azure':
        subscription_id,client_id,secret,tenant_id = data['subscription_id'], data['client_id'], data['secret_id'], data['tenant_id']
        locations, flag = location.get_locations(subscription_id,client_id,secret,tenant_id)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
    elif provider == 'aws':
        access_key, secret_key = data['access_key'], data['secret_key']
        locations, flag = regions.get_locations(access_key,secret_key)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
    elif provider == 'gcp':
        service_account = data['service_account']
        project_id = data['project_id']
        reg, flag = gcpregions.get_regions(service_account, project_id)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': reg})
        else:
            return jsonable_encoder({'status': '500', 'locations': reg, 'message':"wrong credentials"})



