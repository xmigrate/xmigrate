from model.storage import Storage
from utils.id_gen import unique_id_gen
from schemas.storage import StorageCreate, StorageUpdate
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy import Column, update
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
    
    stmt = Storage(
        id = unique_id_gen("storage"),
        bucket_name = data.bucket,
        access_key = data.access_key,
        secret_key = data.secret_key,
        container = data.container,
        project = project_id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )

    db.add(stmt)
    db.commit()
    db.refresh(stmt)

    return JSONResponse({"status": 201, "message": "storage created", "data": [{}]})


def get_storage(project_id: str, db: Session) -> Storage | None:
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


def update_storage(storage_id: str, data: StorageUpdate, db: Session) -> JSONResponse:
    '''
    Update the storage account details.
    
    :param storage: id of the storage
    :param data: storage account details for update
    :param db: active database session
    '''
    
    stmt = update(Storage).where(
        Storage.id==storage_id and Storage.is_deleted==False
    ).values(
        id = unique_id_gen("storage"),
        bucket_name = data.bucket,
        access_key = data.access_key,
        secret_key = data.secret_key,
        container = data.container,
        updated_at = datetime.now()
    ).execution_options(synchronize_session="fetch")

    db.execute(stmt)
    db.commit()

    return JSONResponse({"status": 204, "message": "storage updated", "data": [{}]})