from model.blueprint import *
from utils.converter import *
from utils.database import dbconn
from model.discover import *
from pkg.azure import *
from pkg.common import network as netutils
from pkg.common import build
from pkg.common import hosts as host
import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from quart import request
from quart_jwt_extended import jwt_required
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import Union

router = APIRouter()
executor = ProcessPoolExecutor(max_workers=5)

@router.get('/blueprint')
async def get_blueprint(project: str, db: Session = Depends(dbconn)):
    return jsonable_encoder(db.query(Discover).filter(Discover.project==project).all())

class NetworkCreate(BaseModel):
    project: Union[str,None] = None
    name: Union[str,None] = None
    cidr: Union[str,None] = None

@router.post('/blueprint/network')
async def create_network(data: NetworkCreate, db: Session = Depends(dbconn)):
    network = data.cidr if data.cidr !=None else ''
    project = data.project
    name = data.name

    network_layout_created = netutils.create_nw(project, name, network, db)

    if network_layout_created:
        return  jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500', 'msg': 'Network  creation failed'})


@router.get('/blueprint/network')
async def get_network(project: str, db: Session = Depends(dbconn)):
    return  jsonable_encoder(netutils.fetch_nw(project, db))

class NetworkDelete(BaseModel):
    project: Union[str,None] = None
    nw_name: Union[str,None] = None


@router.delete('/blueprint/network')
async def delete_network(req: NetworkDelete, db: Session = Depends(dbconn)):
    project = req.project
    nw_name = req.nw_name

    if netutils.delete_nw(project, nw_name, db):
        return jsonable_encoder({"msg":"success", "status":200})
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=jsonable_encoder({"msg": "Request couldn't process"}))

class SubnetDelete(BaseModel):
    project: Union[str,None] = None
    subnet_name: Union[str,None] = None
    nw_name: Union[str,None] = None


@router.delete('/blueprint/subnet')
async def delete_subnet(req: SubnetDelete, db: Session = Depends(dbconn)):
    project = req.project
    subnet_name = req.subnet_name
    nw_name = req.nw_name

    if netutils.delete_subnet(project, subnet_name, nw_name, db):
        return jsonable_encoder({"msg":"success", "status":200})
    else:
        return jsonable_encoder({"msg":"failed", "status":500})

@router.get('/blueprint/subnet')
async def get_subnet(network: str, project: str, db: Session = Depends(dbconn)):
    return  jsonable_encoder(netutils.fetch_subnet(project, network, db))

class SubnetCreate(BaseModel):
    project: Union[str,None] = None
    nw_name: Union[str,None] = None
    cidr: Union[str,None] = None
    name: Union[str,None] = None
    nw_type: Union[str,None] = None

@router.post('/blueprint/subnet')
async def create_subnet(data: SubnetCreate, db: Session = Depends(dbconn)):
    network = data.cidr
    project = data.project
    nw_name = data.nw_name
    nw_type = data.nw_type
    name = data.name

    network_layout_created = netutils.create_subnet(network, nw_name, project, nw_type, name, db)

    if network_layout_created:
        return  jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500', 'msg': 'Subnet  creation failed'})
    

@router.get('/blueprint/hosts')
async def get_hosts(project: str, db: Session = Depends(dbconn)):
    return jsonable_encoder(host.fetch_all_hosts(project, db))


@router.post('/blueprint/update')
@jwt_required
async def update_blueprint(db: Session = Depends(dbconn)):
    data = await request.get_json()

    project = data['project']
    machines = data['machines']

    blueprint_updated = host.update_hosts(project, machines, db)

    if blueprint_updated:
        return jsonable_encoder({"msg": "Succesfully updated", "status":200})
    else:
        return jsonable_encoder({"msg": "Couldn't update Blueprint", "status":500})

class BlueprintCreate(BaseModel):
    project: Union[str,None] = None
    machines: Union[list,None] = None

@router.post('/blueprint/create')
async def create_blueprint(data: BlueprintCreate, db: Session = Depends(dbconn)):
    project = data.project
    machines = data.machines
    for machine in machines:
        db.execute(update(Blueprint).where(
            Blueprint.host==machine["hostname"] and Blueprint.project==project
            ).values(
            machine_type=machine["machine_type"], public_route=bool(machine["type"])
            ).execution_options(synchronize_session="fetch"))
        db.commit()
        return jsonable_encoder({"msg":"Succesfully updated","status":200})

class Prepare(BaseModel):
    project: Union[str, None] = None
    hostname: Union[list, None] = None

@router.post('/blueprint/host/prepare')
async def vm_prepare(data: Prepare, db: Session = Depends(dbconn)):
    project = data.project
    hostname = data.hostname
    
    asyncio.create_task(build.call_start_vm_preparation(project, hostname, db))
 
    return jsonable_encoder({"msg": "VM preparation started", "status":200})


class BlueprintHost(BaseModel):
    project: Union[str,None] = None
    hostname: Union[str,None] = None

@router.post('/blueprint/host/clone')
async def image_clone(data: BlueprintHost, db: Session = Depends(dbconn)):
    project = data.project
    hostname = data.hostname

    asyncio.create_task(build.call_start_clone(project, hostname, db))

    return jsonable_encoder({"msg": "Cloning started", "status":200})


@router.post('/blueprint/host/convert')
async def image_convert(data: BlueprintHost, db: Session = Depends(dbconn)):
    project = data.project
    hostname = data.hostname

    asyncio.create_task(build.call_start_convert(project, hostname, db))

    return jsonable_encoder({"msg": "Conversion started", "status":200})

class NetworkBuild(BaseModel):
    project: Union[str,None] = None

@router.post('/blueprint/network/build')
async def network_build(req: NetworkBuild, db: Session = Depends(dbconn)):
    project = req.project
    asyncio.create_task(build.call_build_network(project, db))

    return jsonable_encoder({"msg": "Build started", "status":200})

@router.post('/blueprint/host/build')
async def host_build(data: BlueprintHost):
    project = data.project
    hostname = data.hostname

    asyncio.create_task(build.call_build_host(project,hostname))

    return jsonable_encoder({"msg": "Build started", "status":200})
