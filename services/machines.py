from model.machines import VirtualMachine as VM
from schemas.machines import VMCreate, VMUpdate
from utils.id_gen import unique_id_gen
from datetime import datetime
from typing import Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
from sqlalchemy.orm import Session


def check_vm_exists(hostname: str, blueprint_id: str, db: Session) -> bool:
    '''
    Returns if vm data already exists for a machine in the blueprint.
    
    :param hostname: hostname of the source vm
    :param blueprint_id: id of the corresponding blueprint
    :param db: active database session
    '''

    return(db.query(VM).filter(VM.hostname==hostname, VM.blueprint==blueprint_id, VM.is_deleted==False).count() > 0)


def create_vm(data: VMCreate, db: Session) -> JSONResponse:
    '''
    Creates target vm data.

    :param data: target vm details
    :param db: active database session
    '''

    stmt = VM(
        id = unique_id_gen(data.hostname),
        blueprint = data.blueprint_id,
        hostname = data.hostname,
        network = data.network,
        cpu_core = data.cpu_core,
        cpu_model = data.cpu_model,
        ram = data.ram,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "VM data created", "data": [{}]})


def get_all_machines(blueprint_id: str, db: Session) -> list[VM]:
    '''
    Returns all target vms associated with the blueprint.

    :param hostname: hostname of the source vm
    :param db: active database session
    '''
    return(db.query(VM).filter(VM.blueprint==blueprint_id, VM.is_deleted==False).all())


def get_machineid(hostname: str, blueprint_id: str, db: Session) -> Column[str]:
    '''
    Returns the id for the vm data for a machine in the blueprint.

    :param hostname: hostname of the source vm
    :param blueprint_id: id of the corresponding blueprint
    :param db: active database session
    '''

    return(db.query(VM).filter(VM.hostname==hostname, VM.blueprint==blueprint_id, VM.is_deleted==False).first().id)


def get_machine_by_id(machine_id: str, db: Session) -> VM:
    '''
    Returns the vm data for a single machine in the blueprint.

    :param machine_id: id of the corresponding vm
    :param db: active database session
    '''

    return(db.query(VM).filter(VM.id==machine_id).first())


def get_machine_by_hostname(hostname: str, blueprint_id: str, db: Session) -> Union[VM, None]:
    '''
    Returns the vm data for a single machine in the blueprint.

    :param hostname: hostname of the source vm
    :param blueprint_id: id of the corresponding blueprint
    :param db: active database session
    '''

    return(db.query(VM).filter(VM.hostname==hostname, VM.blueprint==blueprint_id, VM.is_deleted==False).first())


def update_vm(data: VMUpdate, db: Session) -> JSONResponse:
    '''
    Updates target vm data.

    :param data: target vm details
    :param db: active database session
    '''

    vm_data = get_machine_by_id(data.machine_id, db).__dict__
    data_dict = dict(data)
    for key in data_dict.keys():
        if data_dict[key] is None:
            table_key = key.rstrip('_id') if 'blueprint' in key else key
            data_dict[key] = vm_data[table_key]
    data = VMUpdate.parse_obj(data_dict)

    stmt = update(VM).where(
        VM.id==data.machine_id and VM.is_deleted==False
    ).values(
        network = data.network,
        cpu_core = data.cpu_core,
        cpu_model = data.cpu_model,
        ram = data.ram,
        ip = data.ip,
        ip_created = data.ip_created,
        machine_type = data.machine_type,
        public_route = data.public_route,
        status = data.status,
        image_id = data.image_id,
        vm_id = data.vm_id,
        nic_id = data.nic_id,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "VM data updated", "data": [{}]})