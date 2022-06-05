from app import app
import os
import json
from quart import jsonify, request
from pkg.azure import location
from pkg.aws import location as regions
from pkg.gcp import location as gcpregions
from fastapi import Depends
from routes.auth import TokenData, get_current_user
from pydantic import BaseModel
from typing import Union
from fastapi.encoders import jsonable_encoder


class Location(BaseModel):
    provider: Union[str,None] = None
    project_id: Union[str,None] = None
    subscription_id: Union[str,None] = None
    client_id: Union[str,None] = None
    secret_id: Union[str,None] = None
    tenant_id: Union[str,None] = None
    secret_key: Union[str,None] = None
    access_key: Union[str,None] = None
    service_account: Union[str,None] = None


@app.post('/locations')
async def locations_get(data: Location, current_user: TokenData = Depends(get_current_user)):
    provider = data.provider
    if provider == 'azure':
        subscription_id,client_id,secret,tenant_id = data.subscription_id, data.client_id, data.secret_id, data.tenant_id
        locations, flag = location.get_locations(subscription_id,client_id,secret,tenant_id)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
    elif provider == 'aws':
        access_key, secret_key = data.access_key, data.secret_key
        locations, flag = regions.get_locations(access_key,secret_key)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': locations})
        else:
            return jsonable_encoder({'status': '500', 'locations': locations, 'message':"wrong credentials"})
    elif provider == 'gcp':
        service_account = data.service_account
        project_id = data.project_id
        reg, flag = gcpregions.get_regions(service_account, project_id)
        if flag:
            return jsonable_encoder({'status': '200', 'locations': reg})
        else:
            return jsonable_encoder({'status': '500', 'locations': reg, 'message':"wrong credentials"})
