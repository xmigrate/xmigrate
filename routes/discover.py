from __main__ import app
from utils.dbconn import *
from model.discover import *
from model.project import *
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
    current_dir = os.getcwd()
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        nodes = data["hosts"]
        username = data["username"]
        password = data["password"]
        project = data["project"]
        load_dotenv()
        mongodb = os.getenv('MONGO_DB')
        if n.add_nodes(nodes,username,password, project) == False:
            return jsonify({'status': '500'})
    if provider == "aws":
        proj_details = Project.objects(name=project)[0]
        access_key = proj_details['access_key']
        secret_key = proj_details['secret_key']
        location = proj_details['location']
        credentials_str = '['+project+']\naws_access_key_id = '+ access_key+'\n'+ 'aws_secret_access_key = '+secret_key
        if not os.path.exists('/root/.aws'):
            os.mkdir('/root/.aws')
        with open('/root/.aws/credentials', 'w+') as writer:
            writer.write(credentials_str)
        config_str = '[profile '+project+']\nregion = '+location+'\noutput = json'
        with open('/root/.aws/config', 'w+') as writer:
            writer.write(config_str)
        
        os.popen('ansible-playbook -i '+current_dir+'/ansible/+'project+'/hosts ./ansible/aws/xmigrate.yaml -e "mongodb='+mongodb+' project='+project+'" --user '+username+' --become-user '+username+' --become-method sudo > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    elif provider == "azure":
        os.popen('ansible-playbook -i '+current_dir+'/ansible/+'project+'/hosts ./ansible/azure/xmigrate.yaml -e "mongodb='+mongodb+' project='+project+'" --user '+username+' --become-user '+username+' --become-method sudo > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    return jsonify({'status': '500'})
