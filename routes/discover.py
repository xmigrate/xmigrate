from __main__ import app
from utils.dbconn import *
from model.discover import *
from pkg.common import nodes as n
import os
from quart import jsonify, request

@app.route('/discover',methods=['POST','GET'])
async def discover():
    con = create_db_con()
    Discover.objects.delete()
    con.close()
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        nodes = data["hosts"]
        username = data["username"]
        password = data["password"]
        project = data["project"]
        if n.add_nodes(nodes,username,password) == False:
            return jsonify({'status': '500'})
    if provider == "aws":
        os.popen('ansible-playbook ./ansible/aws/env_setup.yaml > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    elif provider == "azure":
        os.popen('ansible-playbook ./ansible/azure/azure_env_setup_ubuntu.yaml -e "project="'+project+' > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    return jsonify({'status': '500'})
