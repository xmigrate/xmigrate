from model.blueprint import Blueprint
from model.discover import Discover
from utils.database import dbconn
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import Union

router = APIRouter()

@router.get("/master/status")
async def get_master_status():
    return jsonable_encoder({'status': '200'})

class MasterUpdate(BaseModel):
    table: str
    host: str
    project: str
    status: Union[str, None] = None
    disk_clone: Union[list, None] = None

@router.post("/master/status/update")
async def master_status_update(data: MasterUpdate, db: Session = Depends(dbconn)):
    try:
        if data.table == 'Blueprint':
            if data.status is not None:
                db.execute(update(Blueprint).where(
                    Blueprint.host==data.host and Blueprint.project==data.project
                    ).values(
                    status=data.status
                    ).execution_options(synchronize_session="fetch"))
                db.commit()
            elif data.disk_clone is not None:
                db.execute(update(Blueprint).where(
                    Blueprint.host==data.host and Blueprint.project==data.project
                    ).values(
                    disk_clone=data.disk_clone
                    ).execution_options(synchronize_session="fetch"))
                db.commit()
    except Exception as e:
        print(e)
        return jsonable_encoder({'status': '500', 'message': str(e)})
    return jsonable_encoder({'status': '200'})


@router.get("/master/disks/get/{project}/{hostname}")
async def get_disks(project, hostname, db: Session = Depends(dbconn)):
    disks = []
    try:
        disks = (db.query(Discover).filter(Discover.host==hostname, Discover.project==project).first()).disk_details
    except Exception as e:
        print(e)
        return jsonable_encoder({'status': '500', 'message': str(e)})
    return jsonable_encoder({'status': '200', 'data': disks})


@router.get("/master/blueprint/get/{project}/{hostname}")
async def get_blueprint_api(project, hostname, db: Session = Depends(dbconn)):
    disks = []
    try:
        disks = (db.query(Blueprint).filter(Blueprint.host==hostname, Blueprint.project==project).first()).disk_clone
    except Exception as e:
        print(e)
        return jsonable_encoder({'status': '500', 'message': str(e)})
    return jsonable_encoder({'status': '200', 'data': disks})
