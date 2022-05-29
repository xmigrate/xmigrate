from app import app
import os
from platform import machine
from quart import jsonify, request
from pkg.azure import compute
from pkg.aws import ec2
from pkg.gcp import compute as gce
from quart_jwt_extended import jwt_required, get_jwt_identity
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from routes.auth import TokenData, get_current_user
from model.project import *
from utils.dbconn import *

@app.get('/vms')
async def vms_get(project: str, current_user: TokenData = Depends(get_current_user)):
    con = create_db_con()
    provider = Project.objects(name=project)[0]['provider']
    con.close()
    if provider == 'azure':
        machine_types, flag = compute.get_vm_types(project)
    elif provider == 'aws':
        machine_types, flag = ec2.get_vm_types(project)
    elif provider == 'gcp':
        machine_types, flag = gce.get_vm_types(project)
    if flag:
        return jsonable_encoder({'status': '200', 'machine_types': machine_types})
    else:
        return jsonable_encoder({'status': '500', 'machine_types': machine_types, 'message':"wrong credentials or location, please check logs"})  
