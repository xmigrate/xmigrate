import os
from app import app
from utils.dbconn import *
from utils.converter import *
from utils.playbook import run_playbook
from model.discover import *
from model.blueprint import *
from pkg.azure import *
from pkg.common import network as netutils
from pkg.common import build as build
from pkg.common import hosts as host
from quart import jsonify, request, make_push_promise
import json
import asyncio
from pkg.azure import disk
from concurrent.futures import ProcessPoolExecutor
from quart_jwt_extended import jwt_required, get_jwt_identity
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from routes.auth import TokenData, get_current_user
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi import Depends
from typing import Union
from fastapi import Depends, HTTPException, status

executor = ProcessPoolExecutor(max_workers=5)

@app.get('/blueprint')
async def get_blueprint(project: str, current_user: TokenData = Depends(get_current_user)):
    con = create_db_con()
    return jsonable_encoder([dict(x) for x in Discover.objects(project=project).allow_filtering()])

class NetworkCreate(BaseModel):
    project: Union[str,None] = None
    name: Union[str,None] = None
    cidr: Union[str,None] = None

@app.post('/blueprint/network')
async def create_network(data: NetworkCreate, current_user: TokenData = Depends(get_current_user)):
    network = data.cidr if data.cidr !=None else ''
    project = data.project
    name = data.name
    network_layout_created = netutils.create_nw(project,name,network)
    if network_layout_created:
        return  jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500', 'msg': 'Network  creation failed'})
    return  jsonable_encoder({'status': '500', 'msg': 'Network creation failed'})


@app.get('/blueprint/network')
async def get_network(project: str, current_user: TokenData = Depends(get_current_user)):
    return  jsonable_encoder(netutils.fetch_nw(project))

class NetworkDelete(BaseModel):
    project: Union[str,None] = None
    nw_name: Union[str,None] = None


@app.delete('/blueprint/network')
async def delete_network(req: NetworkDelete, current_user: TokenData = Depends(get_current_user)):
    project = req.project
    nw_name = req.nw_name
    print(project)
    print(nw_name)
    if netutils.delete_nw(project,nw_name):
        return jsonable_encoder({"msg":"success", "status":200})
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder(
            {"msg": "Request couldn't process"}))

class SubnetDelete(BaseModel):
    project: Union[str,None] = None
    subnet_name: Union[str,None] = None
    nw_name: Union[str,None] = None


@app.delete('/blueprint/subnet')
async def delete_subnet(req: SubnetDelete, current_user: TokenData = Depends(get_current_user)):
    project = req.project
    subnet_name = req.subnet_name
    nw_name = req.nw_name
    if netutils.delete_subnet(project, subnet_name, nw_name):
        return jsonable_encoder({"msg":"success", "status":200})
    else:
        return jsonable_encoder({"msg":"failed", "status":500})

@app.get('/blueprint/subnet')
async def get_subnet(network: str, project: str, current_user: TokenData = Depends(get_current_user)):
    return  jsonable_encoder(netutils.fetch_subnet(project,network))

class SubnetCreate(BaseModel):
    project: Union[str,None] = None
    nw_name: Union[str,None] = None
    cidr: Union[str,None] = None
    name: Union[str,None] = None
    nw_type: Union[str,None] = None

@app.post('/blueprint/subnet')
async def create_subnet(data: SubnetCreate, current_user: TokenData = Depends(get_current_user)):
    network = data.cidr
    project = data.project
    nw_name = data.nw_name
    nw_type = data.nw_type
    name = data.name
    network_layout_created = netutils.create_subnet(network,nw_name,project,nw_type,name)
    print(network_layout_created)
    if network_layout_created:
        return  jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500', 'msg': 'Subnet  creation failed'})
    

@app.get('/blueprint/hosts')
async def get_hosts(project: str, current_user: TokenData = Depends(get_current_user)):
    return jsonable_encoder(host.fetch_all_hosts(project))


@app.route('/blueprint/update', methods=['POST'])
@jwt_required
async def update_blueprint():
    if request.method == 'POST':
        data = await request.get_json()
        project = data['project']
        machines = data['machines']
        blueprint_updated = host.update_hosts(project,machines)
        if blueprint_updated:
            return jsonify({"msg":"Succesfully updated","status":200})
        else:
            return jsonify({"msg":"Cpouldn't update Blueprint","status":500})

class BlueprintCreate(BaseModel):
    project: Union[str,None] = None
    machines: Union[list,None] = None

@app.post('/blueprint/create')
async def create_blueprint(data: BlueprintCreate, current_user: TokenData = Depends(get_current_user)):
    project = data.project
    machines = data.machines
    con = create_db_con()
    for machine in machines:
        print(machine)
        BluePrint.objects(host=machine['hostname'], project=project).update(machine_type=machine['machine_type'],public_route=bool(machine['type']))
    con.shutdown()
    return jsonable_encoder({"msg":"Succesfully updated","status":200})

class Prepare(BaseModel):
    project: Union[str,None] = None
    hostname: Union[list,None] = None

@app.post('/blueprint/host/prepare')
async def vm_prepare(data: Prepare, current_user: TokenData = Depends(get_current_user)):

    project = data.project
    hostname = data.hostname
    con = create_db_con()
    asyncio.create_task(build.call_start_vm_preparation(project=project, hostname=hostname))
 
    return jsonable_encoder({"msg": "VM preparation started", "status":200})


class BlueprintHost(BaseModel):
    project: Union[str,None] = None
    hostname: Union[str,None] = None

class check(BaseModel):
    project: Union[str,None] = None
    hostname: Union[str,None] = None

@app.post('/blueprint/host/check')
async def vm_check(data: check, current_user: TokenData = Depends(get_current_user)):
    print(data)
    project = data.project
    con = create_db_con()
    # run_playbook(provider="aws",project=project,username="ubuntu",curr_working_dir=os.getcwd(),extra_vars=extra_vars)
    asyncio.create_task(build.call_start_check(project))
    return jsonable_encoder({"msg":"Checking started","status":200})


@app.post('/blueprint/host/clone')
async def image_clone(data: BlueprintHost, current_user: TokenData = Depends(get_current_user)):
    project = data.project
    hostname = data.hostname
    asyncio.create_task(build.call_start_clone(project, hostname))
    return jsonable_encoder({"msg":"Cloning started","status":200})


@app.post('/blueprint/host/convert')
async def image_convert(data: BlueprintHost, current_user: TokenData = Depends(get_current_user)):
    project = data.project
    hostname = data.hostname
    asyncio.create_task(build.call_start_convert(project,hostname))
    return jsonable_encoder({"msg":"Build started","status":200})

class NetworkBuild(BaseModel):
    project: Union[str,None] = None

@app.post('/blueprint/network/build')
async def network_build(req: NetworkBuild, current_user: TokenData = Depends(get_current_user)):
    project = req.project
    asyncio.create_task(build.call_build_network(project))
    return jsonable_encoder({"msg":"Build started","status":200})

@app.post('/blueprint/host/build')
async def host_build(data: BlueprintHost, current_user: TokenData = Depends(get_current_user)):
    project = data.project
    hostname = data.hostname
    asyncio.create_task(build.call_build_host(project,hostname))
    return jsonable_encoder({"msg":"Build started","status":200})
