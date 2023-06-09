from utils.log_reader import read_logs
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder


router = APIRouter()

@router.get('/stream')
async def stream(project):
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
    return jsonable_encoder({'line': line,'offset': offset, 'blueprint_status': blueprint_status})