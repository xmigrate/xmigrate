from utils.logger import *
from fastapi.encoders import jsonable_encoder

def internal_server_error(msg):
    logger(msg, "error")
    return jsonable_encoder({'status': '500', 'message': str(msg)}), 500

def page_not_found(msg):
    return jsonable_encoder({'status': '404', 'message': str(msg)}), 404

def bad_request(msg):
    return jsonable_encoder({'status': '400', 'message': str(msg)}), 400