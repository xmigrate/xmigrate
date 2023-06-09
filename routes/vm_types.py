from pkg.common.vm_types import get_vm_types
from routes.auth import get_current_user, TokenData
from utils.database import dbconn
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.get('/vms')
async def vms_get(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    machine_types, flag = get_vm_types(current_user['username'], project, db)
    if flag:
        return jsonable_encoder({'status': '200', 'machine_types': machine_types})
    else:
        return jsonable_encoder({'status': '500', 'machine_types': machine_types, 'message':"wrong credentials or location, please check logs"})  
