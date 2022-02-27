from ansible.playbook import Playbook
import ast
import json
import os
from pygtail import Pygtail
from collections import defaultdict
import boto3
import sys
from quart import Quart, g, request
from quart_cors import cors
from quart_jwt_extended import JWTManager

sys.path.append('./')

app = Quart(__name__)

app = cors(app, allow_origin="*")

app.config['JWT_SECRET_KEY'] = 'try2h@ckT415'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
jwt = JWTManager(app)


#app.secret_key = getenv("SECRET")


from routes.stream import *
from routes.status import *
from routes.server import *
from routes.index import *
from routes.discover import *
from routes.cloning import *
from routes.build import *
from routes.blueprint import *
from routes.project import *
from routes.storage import *
from routes.auth import *
from routes.locations import *
from routes.vm_types import *
from routes.test import *

#Exception
from exception import exception
app.register_error_handler(404, exception.page_not_found)
app.register_error_handler(Exception, exception.internal_server_error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
