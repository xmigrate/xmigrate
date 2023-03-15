from app import app
from quart import jsonify
from utils.log_reader import *
from quart_jwt_extended import jwt_required, get_jwt_identity
from fastapi import Depends
from routes.auth import TokenData, get_current_user
from fastapi.encoders import jsonable_encoder

@app.get('/stream')
async def stream(project, current_user: TokenData = Depends(get_current_user)):
    line = ''
    line = await read_logs(project)
    offset= ''
    blueprint_status = ''
    if "PLAY RECAP" in line:
        offset = "EOF"
        if "unreachable=0" in line:
            if "failed=0" in line:
                blueprint_status = "success"
        else:
            blueprint_status = "failure" 
    return jsonable_encoder({'line':line,'offset':offset, 'blueprint_status':blueprint_status})