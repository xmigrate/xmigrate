from __main__ import app
from utils.dbconn import *
from utils.converter import *
from model.discover import *
from model.blueprint import *
from pkg.azure import *
from pkg.common import network as netutils
from pkg.common import build as build
from flask import render_template, Flask, jsonify, flash, request
import json

@app.route('/blueprint')
def blueprint():
    con = create_db_con()
    return '{'+Discover.objects.to_json()+'}'


@app.route('/blueprint/network/create', methods=['POST'])
def update_blueprint_nw():
    if request.method == 'POST':
        network = request.get_json()['cidr']
        project = request.get_json()['project']
        print(project)
        network_layout_created = netutils.create_nw_layout(network,project)
        if network_layout_created:
            return jsonify({'status': '200', 'blueprint': BluePrint.objects(project=project).to_json()})
        else:
            return jsonify({'status': '500', 'msg': 'Network layout creation failed'})
    return jsonify({'status': '500', 'msg': 'Update blueprint network failed'})


@app.route('/blueprint/build', methods=['POST'])
def build_blueprint():
    if request.method == 'POST':
        project = request.get_json()['project']
        build_completed = build.start_build(project)
        return jsonif({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})

