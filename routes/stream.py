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
        if all(word in line for word in ["unreachable=0", "failed=0"]):
            blueprint_status = "success"
        else:
            blueprint_status = "failure" 
    return jsonable_encoder({'line': line,'offset': offset, 'blueprint_status': blueprint_status})