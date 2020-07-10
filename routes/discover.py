from __main__ import app
from utils.dbconn import *
from model.discover import *
import os
from flask import jsonify, request

@app.route('/discover',methods=['POST','GET'])
def discover():
    con = create_db_con()
    Discover.objects.delete()
    con.close()
    if request.method == 'POST':
        provider = request.get_json()['provider']
        return jsonify({'status': '500'})
    if provider == "aws":
        os.popen('ansible-playbook ../ansible/aws/env_setup.yaml > ../logs/ansible/log.txt')
        return jsonify({'status': '200'})
    elif provider == "azure":
        os.popen('ansible-playbook ../ansible/azure/azure_env_setup_ubuntu > ../logs/ansible/log.txt')
        return jsonify({'status': '200'})
    return jsonify({'status': '500'})
