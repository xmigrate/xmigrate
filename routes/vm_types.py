from __main__ import app
import os
from platform import machine
from quart import jsonify, request
from pkg.azure import compute
from pkg.aws import ec2
from pkg.gcp import compute as gce
from quart_jwt_extended import jwt_required, get_jwt_identity
from model.project import *
from utils.dbconn import *

@app.route('/vms/get', methods=['GET'])
@jwt_required
async def vms_get():
    if request.method == 'GET':
        con = create_db_con()
        project = request.args.get('project')
        provider = Project.objects(name=project)[0]['provider']
        con.close()
        if provider == 'azure':
            machine_types, flag = compute.get_vm_types(project)
        elif provider == 'aws':
            machine_types, flag = ec2.get_vm_types(project)
        elif provider == 'gcp':
            machine_types, flag = gce.get_vm_types(project)
        if flag:
            return jsonify({'status': '200', 'machine_types': machine_types})
        else:
            return jsonify({'status': '500', 'machine_types': machine_types, 'message':"wrong credentials or location, please check logs"})  
    else:
        return jsonify({'status': '500', 'machine_types': machine_types, 'message':"wrong method"})