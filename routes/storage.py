from __main__ import app
import os
from quart import jsonify, request
from pkg.azure import storage as st
from quart_jwt_extended import jwt_required, get_jwt_identity


@app.route('/storage/create', methods=['POST'])
@jwt_required
async def storage_create():
    if request.method == 'POST':
        data = await request.get_json()
        project  = data['project']
        storage = data['storage']
        container = data['container']
        access_key = data['access_key']
        storage_created = st.create_storage(project, storage, container, access_key)
        if storage_created:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})

@app.route('/storage/get', methods=['GET'])
@jwt_required
async def storage_get():
    if request.method == 'GET':
        name = request.args.get('project')
        return jsonify(st.get_storage(name))


@app.route('/storage/update', methods=['POST'])
@jwt_required
async def storage_update():
    if request.method == 'POST':
        data = await request.get_json()
        project  = data['project']
        storage = data['storage']
        container = data['container']
        access_key = data['access_key']
        storage_updated = st.update_storage(project, storage, container, access_key)
        if storage_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})