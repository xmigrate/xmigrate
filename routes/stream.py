from __main__ import app
from flask import jsonify
from utils.log_reader import *

@app.route('/stream')
def stream():
    line = ''
    line = read_logs()
    return jsonify({'line':line})
