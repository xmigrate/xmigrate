from __main__ import app
from utils.dbconn import *
from utils.converter import *
from model.discover import *
from pkg.azure import *
from pkg.common import *
from flask import render_template, Flask, jsonify, flash, request


@app.route('/blueprint')
def blueprint():
    con = create_db_con()
    return jsonify(Discover.objects.to_json())


@app.route('/blueprint/network/create', methods=['POST'])
def update_blueprint_nw():
    if request.method == 'POST':
        network = request.get_json()['cidr']
        network_layout_created = create_nw_layout(network)
        if network_layout_created:
            return jsonify({'status': '200', 'blueprint': Blueprint.objects.to_json()})
        else:
            return jsonify({'status': '500', 'msg': 'Network layout creation failed'})
    return jsonify({'status': '500', 'msg': 'Update blueprint network failed'})


@app.route('/blueprint/create', methods=['POST'])
def create_blueprint():
    if request.method == 'POST':
        if request.get_json()['provider'] == "azure":
            network = request.get_json()['cidr']
