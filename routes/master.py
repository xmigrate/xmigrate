from model.blueprint import Blueprint
from model.discover import Discover
from model.disk import Disk
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
    data: Union[dict,None] = None
    classType: Union[str,None] = None
    classObj: Union[dict,None] = None


@router.post("/master/status/update")
async def master_status_update(data: MasterUpdate, db: Session = Depends(dbconn)):
    update_data = data.data
    class_type = data.classType
    class_obj = data.classObj

    try:
        if class_type == 'Blueprint':
            db.execute(update(Blueprint).where(
                Blueprint.host==class_obj.get('host') and Blueprint.project==class_obj.get('project')
                ).values(
                **update_data
                ).execution_options(synchronize_session="fetch"))
            db.commit()
        elif class_type == 'Discover':
            db.execute(update(Discover).where(
                Discover.host==class_obj.get('host') and Discover.project==class_obj.get('project')
                ).values(
                **update_data
                ).execution_options(synchronize_session="fetch"))
            db.commit()
        elif class_type == 'Disk':
            db.execute(update(Disk).where(
                Disk.host==class_obj.get('host') and Disk.project==class_obj.get('project') and Disk.mnt_path==class_obj.get('mnt_path')
                ).values(
                **update_data
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
