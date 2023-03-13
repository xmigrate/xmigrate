from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from app import app
import os
from quart import jsonify, request
from pkg.common import project
from quart_jwt_extended import jwt_required, get_jwt_identity
from routes.auth import TokenData, get_current_user
from typing import Union

class ProjectCreate(BaseModel):
    provider: Union[str,None] = None
    location: Union[str,None] = None
    name: Union[str,None] = None
    resource_group: Union[str,None] = None
    subscription_id: Union[str,None] = None
    client_id: Union[str,None] = None
    secret_id: Union[str,None] = None
    tenant_id: Union[str,None] = None
    users: Union[list,None] = None
    access_key: Union[str,None] = None
    secret_key: Union[str,None] = None
    resource_group_created: Union[bool,None] = None
    username: Union[str,None] = None
    password: Union[str,None] = None
    public_ip: Union[list,None] = None
    service_account: Union[dict,None] = None
    gcp_project_id: Union[str,None] = None


@app.post('/project')
async def project_create(data: ProjectCreate, current_user: TokenData = Depends(get_current_user)):
    current_user = current_user['username']
    project_created = await project.create_project(data, current_user)
    if project_created:
        return jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500'})


@app.get('/project')
async def project_get(name: str, current_user: TokenData = Depends(get_current_user)):
    current_user = current_user['username']
    print(current_user)
    print(name)
    return jsonable_encoder(project.get_project(name, current_user))

@app.route('/project/update', methods=['POST'])
@jwt_required
async def project_update():
    if request.method == 'POST':
        data = await request.get_json()
        current_user = get_jwt_identity()
        project_updated = await project.update_project(data, current_user)
        if project_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})

