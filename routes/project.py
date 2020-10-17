from __main__ import app
import os
from quart import jsonify, request
from pkg.common import project
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/project/create', methods=['POST'])
@jwt_required
async def project_create():
    if request.method == 'POST':
        data = await request.get_json()
        project_created = await project.create_project(data, get_jwt_identity())
        if project_created:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})


@app.route('/project/get', methods=['GET'])
@jwt_required
async def project_get():
    if request.method == 'GET':
        name = request.args.get('name')
        current_user = get_jwt_identity()
        return jsonify(project.get_project(name, current_user)), 200
    else:
        return jsonify(msg="method not supported"), 400

@app.route('/project/update', methods=['POST'])
@jwt_required
async def project_update():
    if request.method == 'POST':
        data = await request.get_json()
        current_user = get_jwt_identity()
        project_updated = await project.update_project(data, current_user)
        if project_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})

