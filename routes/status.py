from utils.database import dbconn
from model.blueprint import Blueprint
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

router = APIRouter()

@router.get('/migration/status')
async def migration_status(project: str, db: Session = Depends(dbconn)):
    machines = db.query(Blueprint).filter(Blueprint.project==project).all()
    return jsonable_encoder(machines)
    