from __main__ import app
from quart import jsonify
from utils.log_reader import *
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/stream')
@jwt_required
async def stream():
    line = ''
    line = read_logs()
    offset= ''
    blueprint_status = ''
    if "PLAY RECAP" in line:
        offset = "EOF"
        if "unreachable=0" in line:
            if "failed=0" in line:
                blueprint_status = "success"
        else:
            blueprint_status = "failure" 
    return jsonify({'line':line,'offset':offset, 'blueprint_status':blueprint_status})
