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


import sys

sys.path.append('./')

load_dotenv()


app = Flask(__name__)

app.secret_key = getenv("SECRET")

bucket_name = getenv("BUCKET")

from routes.blueprint import *
from routes.build import *
from routes.cloning import *
from routes.discover import *
from routes.index import *
from routes.server import *
from routes.status import *
from routes.stream import *

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
