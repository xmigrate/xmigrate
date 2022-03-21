from __main__ import app
from utils.dbconn import *
from model.discover import *
from model.project import *
from model.storage import *
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
        print(data)
        provider = data['provider']
        nodes = data["hosts"]
        username = data["username"]
        password = data["password"]
        project = data["project"]
        load_dotenv()
        mongodb = os.getenv('BASE_URL')
        if n.add_nodes(nodes,username,password, project) == False:
            return jsonify({'status': '500'})
    if provider == "aws":
        proj_details = Project.objects(name=project)[0]
        access_key = proj_details['access_key']
        secret_key = proj_details['secret_key']
        location = proj_details['location']
        credentials_str = '['+project+']\naws_access_key_id = '+ access_key+'\n'+ 'aws_secret_access_key = '+secret_key
        aws_dir = os.path.expanduser('~/.aws')
        if not os.path.exists(aws_dir):
            os.mkdir(aws_dir)
        with open(aws_dir+'/credentials', 'w+') as writer:
            writer.write(credentials_str)
        config_str = '[profile '+project+']\nregion = '+location+'\noutput = json'
        with open(aws_dir+'/config', 'w+') as writer:
            writer.write(config_str)
        
        os.popen('ansible-playbook -i '+current_dir+'/ansible/'+project+'/hosts ./ansible/aws/xmigrate.yaml -e "mongodb='+mongodb+' project='+project+'" --user '+username+' --become-user '+username+' --become-method sudo > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    elif provider == "azure":
        os.popen('ansible-playbook -i '+current_dir+'/ansible/'+project+'/hosts ./ansible/azure/xmigrate.yaml -e "mongodb='+mongodb+' project='+project+'" --user '+username+' --become-user '+username+' --become-method sudo > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    elif provider == "gcp":
        storage = GcpBucket.objects(project=project)[0]
        project_id = storage['project_id']
        gs_access_key_id = storage['access_key']
        gs_secret_access_key = storage['secret_key']
        print('ansible-playbook -i '+current_dir+'/ansible/'+project+'/hosts ./ansible/gcp/xmigrate.yaml -e "mongodb='+mongodb+' project='+project+' gs_access_key_id='+gs_access_key_id+' gs_secret_access_key='+gs_secret_access_key+' project_id='+project_id+'" --user '+username+' --become-user '+username+' --become-method sudo > ./logs/ansible/log.txt')
        os.popen('ansible-playbook -i '+current_dir+'/ansible/'+project+'/hosts ./ansible/gcp/xmigrate.yaml -e "mongodb='+mongodb+' project='+project+' gs_access_key_id='+gs_access_key_id+' gs_secret_access_key='+gs_secret_access_key+' project_id='+project_id+'" --user '+username+' --become-user '+username+' --become-method sudo > ./logs/ansible/log.txt')
        return jsonify({'status': '200'})
    return jsonify({'status': '500'})
