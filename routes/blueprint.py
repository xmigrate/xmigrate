from pkg.azure import *
from pkg.common import build
from pkg.common import hosts as host
from routes.auth import TokenData, get_current_user
from schemas.common import CommonBase, CommonCreate
from schemas.network import NetworkCreate, NetworkDelete, SubnetCreate, SubnetDelete
from services.blueprint import get_blueprintid
from services.network import (check_network_exists, check_subnet_exists, create_network, create_subnet, delete_network, delete_subnet, get_all_networks, get_all_subnets, get_networkid)
from services.discover import get_discover
from services.project import get_projectid
from utils.database import dbconn
import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from sqlalchemy.orm import Session


router = APIRouter()
executor = ProcessPoolExecutor(max_workers=5)

@router.get('/blueprint')
async def get_blueprint(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    return get_discover(project_id, db)


@router.post('/blueprint/network')
async def network_create(data: NetworkCreate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        data.cidr = data.name if data.cidr is None else data.cidr
        project_id = get_projectid(current_user['username'], data.project, db)
        blueprint_id = get_blueprintid(project_id, db)
        network_exists = check_network_exists(blueprint_id, data.cidr, db)
        if not network_exists:
            create_network(blueprint_id, data, db)
        else:
            print(f'Network {data.name} already exists for the project!')
    except Exception as e:
        print(str(e))
        return jsonable_encoder({'status': '500', 'msg': 'network  creation failed'})


@router.get('/blueprint/network')
async def network_get(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    blueprint_id = get_blueprintid(project_id, db)
    return get_all_networks(blueprint_id, db)


@router.delete('/blueprint/network')
async def network_delete(data: NetworkDelete, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], data.project, db)
    blueprint_id = get_blueprintid(project_id, db)
    try:
        delete_network(blueprint_id, data.cidr, db)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))


@router.delete('/blueprint/subnet')
async def subnet_delete(data: SubnetDelete, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], data.project, db)
        blueprint_id = get_blueprintid(project_id, db)
        network_id = get_networkid(data.cidr, blueprint_id, db)
        delete_subnet(network_id, data.subnet_cidr, db)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))


@router.get('/blueprint/subnet')
async def subnet_get(cidr: str, project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    blueprint_id = get_blueprintid(project_id, db)
    network_id = get_networkid(cidr, blueprint_id, db)
    return get_all_subnets(network_id, db)


@router.post('/blueprint/subnet')
async def subnet_create(data: SubnetCreate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], data.project, db)
        blueprint_id = get_blueprintid(project_id, db)
        network_id = get_networkid(data.nw_cidr, blueprint_id, db)
        subnet_exists = check_subnet_exists(network_id, data.cidr, db)
        if not subnet_exists:
            create_subnet(network_id, data, db)
        else:
            print(f'Subnet with cidr {data.cidr} already exists for the network {data.nw_cidr}!')
    except:
        return jsonable_encoder({'status': '500', 'msg': 'subnet  creation failed'})
    

@router.get('/blueprint/hosts')
async def get_hosts(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    return jsonable_encoder(host.fetch_all_hosts(current_user['username'], project, db))


@router.post('/blueprint/update')
async def update_blueprint(request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        data = await request.body()
        return host.update_hosts(current_user['username'], data['project'], data['machines'], db)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))

# class BlueprintCreate(BaseModel):
#     project: Union[str,None] = None
#     machines: Union[list,None] = None

# @router.post('/blueprint/create')
# async def create_blueprint(data: BlueprintCreate, db: Session = Depends(dbconn)):
#     project = data.project
#     machines = data.machines
#     for machine in machines:
#         db.execute(update(Blueprint).where(
#             Blueprint.host==machine["hostname"] and Blueprint.project==project
#             ).values(
#             machine_type=machine["machine_type"], public_route=bool(machine["type"])
#             ).execution_options(synchronize_session="fetch"))
#         db.commit()
#         return jsonable_encoder({"msg":"Succesfully updated","status":200})


@router.post('/blueprint/host/prepare')
async def vm_prepare(data: CommonCreate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):    
    asyncio.create_task(build.start_vm_preparation(current_user['username'], data.project, data.hostname, db))
    return jsonable_encoder({"message": "vm preparation started", "status": 200})


@router.post('/blueprint/host/clone')
async def image_clone(data: CommonCreate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    asyncio.create_task(build.call_start_clone(current_user['username'], data.project, data.hostname, db))
    return jsonable_encoder({"message": "cloning started", "status":200})


@router.post('/blueprint/host/convert')
async def image_convert(data: CommonCreate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    asyncio.create_task(build.call_start_convert(current_user['username'], data.project, data.hostname, db))
    return jsonable_encoder({"message": "conversion started", "status": 200})


@router.post('/blueprint/network/build')
async def network_build(data: CommonBase, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    asyncio.create_task(build.call_build_network(current_user['username'], data.project, db))
    return jsonable_encoder({"message": "build started", "status": 200})


@router.post('/blueprint/host/build')
async def host_build(data: BlueprintHost, db: Session = Depends(dbconn)):
    project = data.project
    hostname = data.hostname

    asyncio.create_task(build.call_build_host(project, hostname, db))

    return jsonable_encoder({"msg": "Build started", "status":200})
