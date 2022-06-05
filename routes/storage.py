from app import app
import os
from pkg.azure import storage as st
from pkg.aws import bucket as bk
from pkg.gcp import bucket as gbk
from app import app
import os
from pkg.azure import storage as st
from pkg.aws import bucket as bk
from pkg.gcp import bucket as gbk

from routes.auth import TokenData, get_current_user
from typing import Union
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Storage(BaseModel):
    provider: Union[str,None] = None
    project: Union[str,None] = None
    storage: Union[str,None] = None
    storage: Union[str,None] = None
    container: Union[str,None] = None
    access_key: Union[str,None] = None
    secret_key: Union[str,None] = None
    bucket: Union[str,None] = None

@app.post('/storage')
async def storage_create(data: Storage, current_user: TokenData = Depends(get_current_user)):
    provider = data.provider
    project = data.project
    if provider == 'azure':
        storage = data.storage
        container = data.container
        access_key = data.access_key
        storage_created = st.create_storage(
            project, storage, container, access_key)
    elif provider == 'aws':
        bucket = data.bucket
        secret_key = data.secret_key
        access_key = data.access_key
        storage_created = bk.create_bucket(
            project, bucket, secret_key, access_key)
    elif provider == 'gcp':
        bucket = data.bucket
        secret_key = data.secret_key
        access_key = data.access_key
        storage_created = gbk.create_bucket(project, bucket, access_key,secret_key)
    if storage_created:
        return jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500'})


@app.get('/storage')
async def storage_get(project: str, provider:str, current_user: TokenData = Depends(get_current_user)):
    if provider == "azure":
        return jsonable_encoder(st.get_storage(project))
    elif provider == "aws":
        return jsonable_encoder(bk.get_storage(project))
    elif provider == "gcp":
        return jsonable_encoder(gbk.get_storage(project))


@app.post('/storage/update')
async def storage_update(data: Storage, current_user: TokenData = Depends(get_current_user)):
    project = data.project
    provider = data.provider
    if provider == 'azure':
        storage = data.storage
        container = data.container
        access_key = data.access_key
        storage_updated = st.update_storage(
            project, storage, container, access_key)
    elif provider == "aws":
        bucket = data.bucket
        secret_key = data.secret_key
        access_key = data.access_key
        storage_updated = bk.update_bucket(
            project, bucket, secret_key, access_key)
    elif provider == 'gcp':
        bucket = data.bucket
        secret_key = data.secret_key
        access_key = data.access_key
        storage_updated = gbk.update_bucket(
            project, bucket, access_key,secret_key)
    if storage_updated:
        return jsonable_encoder({'status': '200'})
    else:
        return jsonable_encoder({'status': '500'})
