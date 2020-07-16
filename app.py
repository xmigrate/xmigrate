from dotenv import load_dotenv
from os import getenv
from ansible.playbook import Playbook
import ast
import json
import os
from pygtail import Pygtail
from collections import defaultdict
import boto3
from flask import Flask
from flask_cors import CORS
import sys

sys.path.append('./')

load_dotenv()


app = Flask(__name__)
# CORS()
CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
