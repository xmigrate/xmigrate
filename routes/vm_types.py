from pkg.common.vm_types import get_vm_types
from routes.auth import get_current_user, TokenData
from services.project import get_project_by_name
from test_header_files.test_data import get_test_data
from utils.database import dbconn
from fastapi import Depends, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.get('/vms')
async def vms_get(project: str, request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    test_header = request.headers.get("Xm-test")
    if test_header is not None:
        provider = get_project_by_name(current_user['username'], project, db).provider
        test_data = await get_test_data()
        return jsonable_encoder({'status': '200', 'machine_types': test_data[f"{provider}_machine_types"]})
    else:
        machine_types, flag = get_vm_types(current_user['username'], project, db)
        if flag:
            return jsonable_encoder({'status': '200', 'machine_types': machine_types})
        else:
            return jsonable_encoder({'status': '500', 'machine_types': machine_types, 'message':"wrong credentials or location, please check logs"})
