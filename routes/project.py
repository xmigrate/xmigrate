from __main__ import app
import os
from flask import jsonify, request
from pkg.common import project


@app.route('/project/create', methods=['POST'])
def project_create():
    if request.method == 'POST':
        provider = request.get_json()['provider']
        location = request.get_json()['location']
        name = request.get_json()['name']
        rg = request.get_json()['resource_group']
        subid = request.get_json()['subscription_id']
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
def project_update():
    if request.method == 'POST':
        provider = request.get_json()['provider']
        location = request.get_json()['location']
        name = request.get_json()['name']
        rg = request.get_json()['resource_group']
        subid = request.get_json()['subscription_id']
        project_updated = project.update_project(provider, location, name, rg, subid)
        if project_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})
