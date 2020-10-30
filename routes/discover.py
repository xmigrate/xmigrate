from __main__ import app
from utils.dbconn import *
from model.discover import *
from pkg.common import nodes as n
import os
from quart import jsonify, request
from quart_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv
from os import getenv

@app.route('/discover',methods=['POST','GET'])
@jwt_required
async def discover():
    con = create_db_con()
    con.close()
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        nodes = data["hosts"]
        username = data["username"]
        password = data["password"]
        project = data["project"]
        load_dotenv()
        mongodb = os.getenv('MONGO_DB')
        if n.add_nodes(nodes,username,password) == False:
            return jsonify({'status': '500'})
    if provider == "aws":
        os.popen('ansible-playbook ./ansible/aws/env_setup.yaml > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    elif provider == "azure":
        os.popen('ansible-playbook ./ansible/azure/azure_env_setup_ubuntu.yaml -e "mongodb='+mongodb+' project='+project+'" > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    return jsonify({'status': '500'})
