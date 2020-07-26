from __main__ import app
import os
from quart import jsonify, request
from pkg.azure import storage as st


@app.route('/storage/create', methods=['POST'])
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
def storage_get():
    if request.method == 'GET':
        name = request.args.get('name')
        return jsonify(st.get_storage(name))


@app.route('/storage/update', methods=['POST'])
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