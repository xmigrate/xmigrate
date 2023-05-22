from model.project import Project
from pkg.aws import ec2
from pkg.azure import compute
from pkg.gcp import compute as gce
from utils.database import dbconn
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/vms')
async def vms_get(project: str, db: Session = Depends(dbconn)):
    provider = (db.query(Project).filter(Project.name==project).first()).provider

    if provider == 'azure':
        machine_types, flag = compute.get_vm_types(project, db)
    elif provider == 'aws':
        machine_types, flag = ec2.get_vm_types(project, db)
    elif provider == 'gcp':
        machine_types, flag = gce.get_vm_types(project, db)
    if flag:
        return jsonable_encoder({'status': '200', 'machine_types': machine_types})
    else:
        return jsonable_encoder({'status': '500', 'machine_types': machine_types, 'message':"wrong credentials or location, please check logs"})  
