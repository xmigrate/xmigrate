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
executor = ProcessPoolExecutor(max_workers=5)

@app.route('/blueprint')
def blueprint():
    con = create_db_con()
    return Discover.objects.to_json()


@app.route('/blueprint/network/create', methods=['POST'])
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
async def get_nw():
    if request.method == 'GET':
        data = await request.get_json()
        project = data['project']
        return  jsonify(netutils.fetch_nw(project))

@app.route('/blueprint/subnet/get', methods=['GET'])
async def get_subnet():
    if request.method == 'GET':
        data = await request.get_json()
        network = data['network']
        project = data['project']
        return  jsonify(netutils.fetch_subnet(project,network))

@app.route('/blueprint/subnet/create', methods=['POST'])
async def create_subnet():
    if request.method == 'POST':
        data = await request.get_json()
        network = data['cidr']
        project = data['project']
        nw_name = data['nw_name']
        nw_type = data['nw_type']
        name = data['name']
        network_layout_created = netutils.create_subnet(network,nw_name,project,nw_type,name)
        if network_layout_created:
            return  jsonify({'status': '200'})
        else:
            return jsonify({'status': '500', 'msg': 'Subnet  creation failed'})
    return  jsonify({'status': '500', 'msg': 'Subnet creation failed'})


@app.route('/blueprint/hosts/get', methods=['GET'])
async def get_hosts():
    if request.method == 'GET':
        data = await request.get_json()
        project = data['project']
        return jsonify(host.fetch_hosts(project))


@app.route('/blueprint/update', methods=['POST'])
async def update_blueprint():
    if request.method == 'POST':
        data = await request.get_json()
        project = data['project']
        machines = data['machines']
        blueprint_updated = update_hosts(project,machines)
        if blueprint_updated:
            return jsonify({"msg":"Succesfully updated","status":200})
        else:
            return jsonify({"msg":"Cpouldn't update Blueprint","status":500})


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
        asyncio.create_task(build.call_start_build(project))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})


@app.route('/blueprint/image/convert', methods=['POST'])
async def image_convert():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        asyncio.create_task(disk.adhoc_image_conversion(project))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})

@app.route('/blueprint/infra/all', methods=['POST'])
async def infra_build():
    if request.method == 'POST':
        project = await request.get_json()
        project = project['project']
        asyncio.create_task(build.start_infra_build(project))
        return jsonify({"msg":"Build started","status":200})
    else:
        return jsonify({"msg":"cannot read project name","status":500})
