from routes.auth import TokenData, get_current_user
from services.blueprint import get_blueprint
from services.project import get_projectid
from utils.database import dbconn
from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


router = APIRouter()

@router.get('/migration/status')
async def migration_status(project: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(dbconn)):
    project_id = get_projectid(current_user['username'], project, db)
    machines = get_blueprint(project_id, db)
    return jsonable_encoder(machines)