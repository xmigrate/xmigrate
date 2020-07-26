from __main__ import app
from utils.dbconn import *
from utils.converter import *
from model.discover import *
from model.blueprint import *
from pkg.azure import *
from pkg.common import network as netutils
from pkg.common import build as build
from quart import jsonify, request
import json
import asyncio

@app.route('/blueprint')
def blueprint():
    con = create_db_con()
    return Discover.objects.to_json()


@app.route('/blueprint/network/create', methods=['POST'])
async def update_blueprint_nw():
    if request.method == 'POST':
        data = await request.get_json()
        network = data['cidr']
        project = data['project']
        print(project)
        network_layout_created = netutils.create_nw_layout(network,project)
        if network_layout_created:
            return  jsonify({'status': '200', 'blueprint': BluePrint.objects(project=project).to_json()})
        else:
            return jsonify({'status': '500', 'msg': 'Network layout creation failed'})
    return  jsonify({'status': '500', 'msg': 'Update blueprint network failed'})


@app.route('/blueprint/create', methods=['POST'])
async def create_blueprint():
    if request.method == 'POST':
        data = await request.get_json()
        project = data['project']
        machines = data['machines']
        con = create_db_con()
        for machine in machines:
            print(machine)
            BluePrint.objects(host=machine['host']).update(machine_type=machine['machine_type'],public_route=bool(machine['public_route']))
        con.close()
        return jsonify({"msg":"Succesfully updated","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})


@app.route('/blueprint/build', methods=['POST'])
async def build_blueprint():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        await asyncio.create_task(build.start_build(project))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})

