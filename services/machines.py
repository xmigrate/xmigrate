from model.machines import VirtualMachine as VM
from schemas.machines import VMCreate, VMUpdate
from typing import List, Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column
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

    vm = VM()
    vm_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in vm_data.items():
        setattr(vm, key, value)

    db.add(vm)
    db.commit()
    db.refresh(vm)

    return JSONResponse({"status": 201, "message": "VM data created", "data": [{}]}, status_code=201)


def get_all_machines(blueprint_id: str, db: Session) -> List[VM]:
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

    db_vm = get_machine_by_id(data.id, db)
    vm_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in vm_data.items():
        setattr(db_vm, key, value)

    db.add(db_vm)
    db.commit()
    db.refresh(db_vm)

    return JSONResponse({"status": 204, "message": "VM data updated", "data": [{}]}, status_code=204)