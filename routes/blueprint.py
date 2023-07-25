from pkg.azure import *
from pkg.common import build
from pkg.common import hosts as host
from routes.auth import TokenData, get_current_user
from schemas.blueprint import BlueprintCreate
from schemas.common import CommonBase, CommonCreate
from schemas.machines import VMUpdate
from schemas.network import NetworkCreate, NetworkDelete, SubnetCreate, SubnetDelete
from services.blueprint import get_blueprintid
from services.machines import get_machineid, update_vm
from services.network import (check_network_exists, check_subnet_exists, create_network, create_subnet, delete_network, delete_all_subnets, delete_subnet, get_all_networks, get_all_subnets, get_networkid, get_networkid_by_name)
from services.discover import get_discover
from services.project import get_projectid, get_project_by_name
from pkg.test_header_files.test_data import blueprint_save_test_data, network_create_test_data, subnet_create_test_data
from utils.constants import Test
from utils.database import dbconn
import asyncio
from concurrent.futures import ProcessPoolExecutor
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from sqlalchemy.orm import Session


router = APIRouter()
executor = ProcessPoolExecutor(max_workers=5)

@router.get('/blueprint')
async def get_blueprint(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    discover_data = get_discover(project_id, db)
    if discover_data != []:
        discover_data = discover_data[0].__dict__
        discover_data['disk_details'] = json.loads(discover_data['disk_details'])
        discover_data = [discover_data]
    return discover_data


@router.post('/blueprint/network')
async def network_create(data: NetworkCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        data.cidr = data.name if data.cidr is None else data.cidr
        project_id = get_projectid(current_user['username'], data.project, db)
        blueprint_id = get_blueprintid(project_id, db)
        data.blueprint = blueprint_id
        test_header = request.headers.get(Test.HEADER.value)
        if test_header is not None:
            await network_create_test_data(data, db)
            return jsonable_encoder({"msg": "network data saved", "status": 200})
        else:
            network_exists = check_network_exists(blueprint_id, data.cidr, data.name, db)
            if not network_exists:
                create_network(data, db)
            else:
                print(f'Network with cidr ({data.cidr}) and/or name ({data.name}) already exists for the project!')
            for host in data.hosts:
                networks = get_all_networks(blueprint_id, db)
                machine_id = get_machineid(host['hostname'], blueprint_id, db)
                vm_data = VMUpdate(machine_id=machine_id, network=networks[0].cidr)
                update_vm(vm_data, db)
        return jsonable_encoder({'status': '200', 'msg': 'network data saved successfully'})
    except Exception as e:
        print(str(e))
        return jsonable_encoder({'status': '500', 'msg': 'network creation failed'})


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
        network_id = get_networkid_by_name(data.name, blueprint_id, db)
        delete_all_subnets(network_id, db)
        return delete_network(blueprint_id, data.name, db)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))


@router.delete('/blueprint/subnet')
async def subnet_delete(data: SubnetDelete, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], data.project, db)
        blueprint_id = get_blueprintid(project_id, db)
        network_id = get_networkid_by_name(data.name, blueprint_id, db)
        return delete_subnet(network_id, data.subnet_name, db)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))


@router.get('/blueprint/subnet')
async def subnet_get(nw_cidr: str, project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    blueprint_id = get_blueprintid(project_id, db)
    network_id = get_networkid(nw_cidr, blueprint_id, db)
    return get_all_subnets(network_id, db)


@router.post('/blueprint/subnet')
async def subnet_create(data: SubnetCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], data.project, db)
        blueprint_id = get_blueprintid(project_id, db)
        network_id = get_networkid(data.nw_cidr, blueprint_id, db)
        data.network = network_id
        test_header = request.headers.get(Test.HEADER.value)
        if test_header is not None:
            await subnet_create_test_data(data, db)
        else:
            subnet_exists = check_subnet_exists(data.network, data.cidr, data.subnet_name, db)
            if not subnet_exists:
                return create_subnet(data, db)
            else:
                print(f'Subnet with cidr ({data.cidr}) and/or name ({data.subnet_name}) already exists for the network {data.nw_cidr}!')
    except:
        return jsonable_encoder({'status': '500', 'msg': 'subnet  creation failed'})
    

@router.get('/blueprint/hosts')
async def get_hosts(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    return jsonable_encoder(host.fetch_all_hosts(current_user['username'], project, db))


@router.post('/blueprint/update')
async def update_blueprint(request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        data = await request.body()
        data = json.loads(data.decode())
        return host.update_hosts(current_user['username'], data['project'], data['machines'], db)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=jsonable_encoder({"msg": "request couldn't process"}))
    

@router.post('/blueprint/create')
async def create_blueprint(data: BlueprintCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project = get_project_by_name(current_user['username'], data.project, db)
    blueprint_id = get_blueprintid(project.id, db)
    test_header = request.headers.get(Test.HEADER.value)
    if test_header is not None:
        await blueprint_save_test_data(project.provider, blueprint_id, data, db)
    else:
        for machine in data.machines:
            machine_id = get_machineid(machine["hostname"], blueprint_id, db)
            vm_data = VMUpdate(machine_id=machine_id, machine_type=machine['machine_type'], public_route=bool(machine["type"]))
            update_vm(vm_data, db)
    return jsonable_encoder({"msg": "succesfully updated", "status": 200})


@router.post('/blueprint/network/build')
async def network_build(data: CommonBase, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    test_header = True if request.headers.get(Test.HEADER.value) is not None else False
    asyncio.create_task(build.start_network_build(current_user['username'], data.project, db, test_header))
    return jsonable_encoder({"message": "network build started", "status": 200})


@router.post('/blueprint/host/prepare')
async def vm_prepare(data: CommonCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)): 
    test_header = True if request.headers.get(Test.HEADER.value) is not None else False
    asyncio.create_task(build.start_vm_preparation(current_user['username'], data.project, data.hostname, db, test_header))
    return jsonable_encoder({"message": "vm preparation started", "status": 200})


@router.post('/blueprint/host/clone')
async def image_clone(data: CommonCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    test_header = True if request.headers.get(Test.HEADER.value) is not None else False
    asyncio.create_task(build.start_cloning(current_user['username'], data.project, data.hostname, db, test_header))
    return jsonable_encoder({"message": "cloning started", "status":200})


@router.post('/blueprint/host/convert')
async def image_convert(data: CommonCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    test_header = True if request.headers.get(Test.HEADER.value) is not None else False
    asyncio.create_task(build.start_conversion(current_user['username'], data.project, data.hostname, db, test_header))
    return jsonable_encoder({"message": "conversion started", "status": 200})


@router.post('/blueprint/host/build')
async def host_build(data: CommonCreate, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    test_header = True if request.headers.get(Test.HEADER.value) is not None else False
    asyncio.create_task(build.start_host_build(current_user['username'], data.project, data.hostname, db, test_header))
    return jsonable_encoder({"msg": "build started", "status": 200})
