from dotenv import load_dotenv
from os import getenv
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

load_dotenv()


app = Quart(__name__)

app = cors(app, allow_origin="*")

app.config['JWT_SECRET_KEY'] = 'try2h@ckT415'  # Change this!
jwt = JWTManager(app)


app.secret_key = getenv("SECRET")
bucket_name = getenv("BUCKET")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
