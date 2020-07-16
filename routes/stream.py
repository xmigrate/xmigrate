from __main__ import app
from flask import jsonify
from utils.log_reader import *

@app.route('/stream')
def stream():
    line = ''
    line = read_logs()
    offset= ''
    if "PLAY RECAP" in line:
        offset = "EOF"
    return jsonify({'line':line,'offset':offset})
