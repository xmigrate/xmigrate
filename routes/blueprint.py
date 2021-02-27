from __main__ import app
from utils.dbconn import *
from utils.converter import *
from model.discover import *
from model.blueprint import *
from pkg.azure import *
from pkg.common import network as netutils
from pkg.common import build as build
from pkg.common import hosts as host
from quart import jsonify, request, make_push_promise
import json
import asyncio
from pkg.azure import disk
from concurrent.futures import ProcessPoolExecutor
from quart_jwt_extended import jwt_required, get_jwt_identity

executor = ProcessPoolExecutor(max_workers=5)

@app.route('/blueprint')
@jwt_required
async def get_blueprint():
    if request.method == 'GET':
        project = request.args.get('project')
        con = create_db_con()
        return jsonify(Discover.objects(project=project).to_json())
    else:
        return jsonify({"status":500, "msg": "method not supported"})


@app.route('/blueprint/network/create', methods=['POST'])
@jwt_required
async def create_nw():
    if request.method == 'POST':
        data = await request.get_json()
        network = data['cidr']
        project = data['project']
        name = data['name']
        network_layout_created = netutils.create_nw(network,project,name)
        if network_layout_created:
            return  jsonify({'status': '200'})
        else:
            return jsonify({'status': '500', 'msg': 'Network  creation failed'})
    return  jsonify({'status': '500', 'msg': 'Network creation failed'})


@app.route('/blueprint/network/get', methods=['GET'])
@jwt_required
async def get_nw():
    if request.method == 'GET':
        project = request.args.get('project')
        print(project)
        return  jsonify(netutils.fetch_nw(project))


@app.route('/blueprint/network/delete', methods=['GET'])
@jwt_required
async def delete_nw():
    if request.method == 'GET':
        project = request.args.get('project')
        nw_name = request.args.get('nw_name')
        if netutils.delete_nw(project,nw_name):
            return jsonify({"msg":"success", "status":200})
        else:
            return  jsonify({"msg":"failed", "status":500})


@app.route('/blueprint/subnet/delete', methods=['GET'])
@jwt_required
async def delete_subnet():
    if request.method == 'GET':
        project = request.args.get('project')
        subnet_name = request.args.get('subnet_name')
        nw_name = request.args.get('nw_name')
        if netutils.delete_subnet(project, subnet_name, nw_name):
            return jsonify({"msg":"success", "status":200})
        else:
            return  jsonify({"msg":"failed", "status":500})

@app.route('/blueprint/subnet/get', methods=['GET'])
@jwt_required
async def get_subnet():
    if request.method == 'GET':
        network = request.args.get('network')
        project = request.args.get('project')
        return  jsonify(netutils.fetch_subnet(project,network))

@app.route('/blueprint/subnet/create', methods=['POST'])
@jwt_required
async def create_subnet():
    if request.method == 'POST':
        data = await request.get_json()
        network = data['cidr']
        project = data['project']
        nw_name = data['nw_name']
        nw_type = data['nw_type']
        name = data['name']
        network_layout_created = netutils.create_subnet(network,nw_name,project,nw_type,name)
        print(network_layout_created)
        if network_layout_created:
            return  jsonify({'status': '200'})
        else:
            return jsonify({'status': '500', 'msg': 'Subnet  creation failed'})
    

@app.route('/blueprint/hosts/get', methods=['GET'])
@jwt_required
async def get_hosts():
    if request.method == 'GET':
        project = request.args.get('project')
        return jsonify(host.fetch_all_hosts(project))


@app.route('/blueprint/update', methods=['POST'])
@jwt_required
async def update_blueprint():
    if request.method == 'POST':
        data = await request.get_json()
        project = data['project']
        machines = data['machines']
        blueprint_updated = host.update_hosts(project,machines)
        if blueprint_updated:
            return jsonify({"msg":"Succesfully updated","status":200})
        else:
            return jsonify({"msg":"Cpouldn't update Blueprint","status":500})


@app.route('/blueprint/create', methods=['POST'])
@jwt_required
async def create_blueprint():
    if request.method == 'POST':
        data = await request.get_json()
        project = data['project']
        machines = data['machines']
        con = create_db_con()
        for machine in machines:
            print(machine)
            BluePrint.objects(host=machine['hostname']).update(machine_type=machine['machine_type'],public_route=bool(machine['type']))
        con.close()
        return jsonify({"msg":"Succesfully updated","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})


@app.route('/blueprint/build', methods=['POST'])
@jwt_required
async def build_blueprint():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        asyncio.create_task(build.call_start_build(project))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})


@app.route('/blueprint/host/clone', methods=['POST'])
@jwt_required
async def image_convert():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        hostname = project['hostname']
        asyncio.create_task(build.call_start_clone(project,hostname))
        return jsonify({"msg":"Cloning started","status":200})
    else:
        return jsonify({"msg":"Some error occured","status":500})


@app.route('/blueprint/host/convert', methods=['POST'])
@jwt_required
async def image_convert():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        hostname = project['hostname']
        asyncio.create_task(build.call_start_convert(project,hostname))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})

@app.route('/blueprint/host/build', methods=['POST'])
@jwt_required
async def infra_build():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        asyncio.create_task(build.start_infra_build(project))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})
