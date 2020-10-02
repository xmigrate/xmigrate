from __main__ import app
import os
from quart import jsonify, request
from pkg.azure import compute
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/vms/get', methods=['GET'])
@jwt_required
async def vms_get():
    if request.method == 'GET':
        project = request.args.get('project')
        machine_types, flag = compute.get_vm_types(project)
        if flag:
            return jsonify({'status': '200', 'machine_types': machine_types})
        else:
            return jsonify({'status': '500', 'machine_types': machine_types, 'message':"wrong credentials or location, please check logs"})  
    else:
        return jsonify({'status': '500', 'machine_types': machine_types, 'message':"wrong method"})