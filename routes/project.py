from __main__ import app
import os
from flask import jsonify, request
from pkg.common import *


@app.route('/project/create', methods=['POST'])
def project_create():
    if request.method == 'POST':
        provider = request.get_json()['provider']
        location = request.get_json()['location']
        name = request.get_json()['name']
        project_created = create_project(provider, location, name)
        if project_created:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})


@app.route('/project/get', methods=['GET'])
def project_get():
    if request.method == 'GET':
        name = request.args.get('name')
        return jsonify(get_project(name))


@app.route('/project/update', methods=['POST'])
def project_update():
    if request.method == 'POST':
        provider = request.get_json()['provider']
        location = request.get_json()['location']
        name = request.get_json()['name']
        project_updated = update_project(provider, location, name)
        if project_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})
