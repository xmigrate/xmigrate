from routes.auth import TokenData, get_current_user
from schemas.disk import DiskUpdate
from schemas.machines import VMUpdate
from schemas.master import MasterUpdate
from services.blueprint import get_blueprintid
from services.discover import get_discover
from services.disk import get_all_disks, get_diskid, update_disk
from services.machines import get_machineid, update_vm
from services.project import get_projectid
from utils.database import dbconn
import json
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/master/status")
async def get_master_status():
    return jsonable_encoder({'status': '200'})


@router.post("/master/status/update")
async def master_status_update(data: MasterUpdate, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        if data.table == 'Disk':
            project_id = get_projectid(current_user['username'], data.project, db)
            blueprint_id = get_blueprintid(project_id, db)
            machine_id = get_machineid(data.host, blueprint_id, db)

            if data.status is not None:
                vm_data = VMUpdate(machine_id=machine_id, status=data.status)
                update_vm(vm_data, db)      
            elif data.disk_clone is not None:
                disk_id = get_diskid(machine_id, data.mountpoint, db)
                disk_data = DiskUpdate(disk_id=disk_id, disk_clone=data.disk_clone)
                update_disk(disk_data, db)
    except Exception as e:
        print(str(e))
        return jsonable_encoder({'status': '500', 'message': str(e)})
    return jsonable_encoder({'status': '200'})


@router.get("/master/disks/get/{project}")
async def get_disks(project, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], project, db)
        disks = json.loads(get_discover(project_id, db)[0].disk_details)
    except Exception as e:
        print(str(e))
        return jsonable_encoder({'status': '500', 'message': str(e)})
    return jsonable_encoder({'status': '200', 'data': disks})


@router.get("/master/blueprint/get/{project}/{hostname}")
async def get_blueprint_api(project, hostname, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    try:
        project_id = get_projectid(current_user['username'], project, db)
        blueprint_id = get_blueprintid(project_id, db)
        machine_id = get_machineid(hostname, blueprint_id, db)
        disks = [json.loads(host.disk_clone) for host in get_all_disks(machine_id, db)]
    except Exception as e:
        print(str(e))
        return jsonable_encoder({'status': '500', 'message': str(e)})
    return jsonable_encoder({'status': '200', 'data': disks})
