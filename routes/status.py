from app import app
from utils.dbconn import *
from model.blueprint import *
import json
from quart import jsonify,request
from quart_jwt_extended import jwt_required, get_jwt_identity
from fastapi import Depends
from routes.auth import TokenData, get_current_user
from fastapi.encoders import jsonable_encoder

@app.get('/migration/status')
async def migration_status(project: str, current_user: TokenData = Depends(get_current_user)):
    con = create_db_con()
    machines = [dict(x) for x in BluePrint.objects(project=project).allow_filtering()]
    con.shutdown()
    return jsonable_encoder(machines)
