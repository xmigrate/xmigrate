from __main__ import app
from flask import jsonify
from utils.log_reader import *

@app.route('/stream')
def stream():
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
