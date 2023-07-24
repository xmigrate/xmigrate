from model.storage import Storage
from schemas.storage import StorageCreate, StorageUpdate
from typing import Union
from fastapi.responses import JSONResponse
from sqlalchemy import Column
from sqlalchemy.orm import Session


def check_storage_exists(project_id: str, db: Session) -> bool:
    '''
    Returns if a storage account already exists for the given project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''

    return(db.query(Storage).filter(Storage.project==project_id, Storage.is_deleted==False).count() > 0)


def create_storage(project_id: str, data: StorageCreate, db:Session) -> JSONResponse:
    '''
    Stores the storage account credentials for the project.
    
    :param project_id: id of the corresponding project
    :param data: storage account details
    :param db: active database session
    '''
    
    storage = Storage()
    storage_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in storage_data.items():
        setattr(storage, key, value)

    storage.project = project_id

    db.add(storage)
    db.commit()
    db.refresh(storage)

    return JSONResponse({"status": 201, "message": "storage created", "data": [{}]}, status_code=201)


def get_storage(project_id: str, db: Session) -> Union[Storage, None]:
    '''
    Returns the storage account associated with the specified project.
    
    :param project_id: id of the corresponding project
    :param db: active database session
    '''
    return(db.query(Storage).filter(Storage.project==project_id, Storage.is_deleted==False).first())


def get_storageid(project_id: str, db: Session) -> Column[str]:
    '''
    Returns the id for the storage account data of the given project.

    :param project_id: unique id of the project
    :param db: active database session
    '''

    return(db.query(Storage).filter(Storage.project==project_id, Storage.is_deleted==False).first().id)


def get_storage_by_id(storage_id: str, db: Session) -> Storage:
    '''
    Returns the storage account associated with the active project.
    
    :param storage_id: id of the corresponding storage account data
    :param db: active database session
    '''
    
    return(db.query(Storage).filter(Storage.id==storage_id).first())


def update_storage(data: StorageUpdate, db: Session) -> JSONResponse:
    '''
    Update the storage account details.
    
    :param data: storage account details for update
    :param db: active database session
    '''

    db_storage = get_storage_by_id(data.id, db)
    storage_data = data.dict(exclude_none=True, by_alias=False)

    for key, value in storage_data.items():
        setattr(db_storage, key, value)

    db.add(db_storage)
    db.commit()
    db.refresh(db_storage)

    return JSONResponse({"status": 204, "message": "storage updated", "data": [{}]}, status_code=204)