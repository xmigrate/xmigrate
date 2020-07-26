from __main__ import app
import os
from quart import jsonify, request
from pkg.common import project


@app.route('/project/create', methods=['POST'])
async def project_create():
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        location = data['location']
        name = data['name']
        rg = data['resource_group']
        subid = data['subscription_id']
        project_created = project.create_project(provider, location, name, rg, subid)
        if project_created:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})


@app.route('/project/get', methods=['GET'])
def project_get():
    if request.method == 'GET':
        name = request.args.get('name')
        return jsonify(project.get_project(name))


@app.route('/project/update', methods=['POST'])
async def project_update():
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        location = data['location']
        name = data['name']
        rg = data['resource_group']
        subid = data['subscription_id']
        project_updated = project.update_project(provider, location, name, rg, subid)
        if project_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})
