from __main__ import app
from quart import jsonify
from utils.logger import *

def internal_server_error(msg):
    logger(msg,"error")
    return jsonify({'status': '500','message': str(msg)}), 500

def page_not_found(msg):
    return jsonify({'status': '404','message': str(msg)}), 404

def bad_request(msg):
    return jsonify({'status': '400','message': str(msg)}), 400