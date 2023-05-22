from pkg.aws import bucket as bk
from pkg.azure import storage as st
from pkg.gcp import bucket as gbk
from utils.database import dbconn
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Union


class Storage(BaseModel):
    provider: Union[str,None] = None
    project: Union[str,None] = None
    storage: Union[str,None] = None
    storage: Union[str,None] = None
    container: Union[str,None] = None
    access_key: Union[str,None] = None
    secret_key: Union[str,None] = None
    bucket: Union[str,None] = None

router = APIRouter()

@router.post('/storage')
async def storage_create(data: Storage, db: Session = Depends(dbconn)):
    if data.provider == 'azure':
        storage_created = st.create_storage(data.project, data.storage, data.container, data.access_key, db)
    elif data.provider == 'aws':
        storage_created = bk.create_bucket(data.project, data.bucket, data.secret_key, data.access_key, db)
    elif data.provider == 'gcp':
        storage_created = gbk.create_bucket(data.project, data.bucket, data.access_key, data.secret_key, db)

    if storage_created:
        return jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500'})


@router.get('/storage')
async def storage_get(project: str, provider: str, db: Session = Depends(dbconn)):
    if provider == "azure":
        return jsonable_encoder(st.get_storage(project, db))
    elif provider == "aws":
        return jsonable_encoder(bk.get_storage(project, db))
    elif provider == "gcp":
        return jsonable_encoder(gbk.get_storage(project, db))


@router.post('/storage/update')
async def storage_update(data: Storage, db: Session = Depends(dbconn)):
    if data.provider == 'azure':
        storage_updated = st.update_storage(data.project, data.storage, data.container, data.access_key, db)
    elif data.provider == "aws":
        storage_updated = bk.update_bucket(data.project, data.bucket, data.secret_key, data.access_key, db)
    elif data.provider == 'gcp':
        storage_updated = gbk.update_bucket(data.project, data.bucket, data.access_key, data.secret_key, db)

    if storage_updated:
        return jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500'})
