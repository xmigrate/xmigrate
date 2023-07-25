from routes.auth import TokenData, get_current_user
from services.project import get_projectid
from services.storage import (check_storage_exists, create_storage, get_storage, get_storageid, update_storage)
from schemas.storage import StorageCreate, StorageUpdate
from utils.database import dbconn
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()


@router.post('/storage')
async def storage_create(data: StorageCreate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    print(data)
    try:
        project_id = get_projectid(current_user['username'], data.project, db)
        storage_exists = check_storage_exists(project_id, db)
        if not storage_exists:
            return create_storage(project_id, data, db)
        else:
            return jsonable_encoder({"message": f"storage account for project {data.project} already exists!"})
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder({"message": "Couldn't save storage account details!"}))


@router.get('/storage')
async def storage_get(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    return get_storage(project_id, db)


@router.post('/storage/update')
async def storage_update(data: StorageUpdate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], data.project, db)
        storage_id = get_storageid(project_id, db)
        data.id = storage_id
        return update_storage(data, db)
    except Exception as e:
        print(str(e))
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder({"message": "Couldn't update project!"}))
