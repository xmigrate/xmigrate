from __main__ import app
import json
from quart import jsonify

from pkg.gcp import network as gcp_network
from pkg.gcp import location
from pkg.gcp import compute

# remove this once db integration finished
with open('token.json', 'r') as f:
    service_account_json = json.load(f)

project_id = 'maximal-coast-342017'


@app.route('/gcp-test/network/list', methods=['GET'])
async def gcp_network_list():
    return jsonify({'status': '200', 'message': gcp_network.list_vpc(project_id, service_account_json)})


@app.route('/gcp-test/network/create/<network_name>', methods=['GET'])
async def gcp_network_create(network_name):
    # network_name = "test-vpc"
    return jsonify({'status': '200', 'message': gcp_network.create_vpc(project_id, service_account_json, network_name)})


@app.route('/gcp-test/network/get/<network_name>', methods=['GET'])
async def gcp_network_get(network_name):
    return jsonify({'status': '200', 'message': gcp_network.get_vpc(project_id, service_account_json, network_name)})


@app.route('/gcp-test/network/delete/<network_name>', methods=['GET'])
async def gcp_network_delete(network_name):
    return jsonify({'status': '200', 'message': gcp_network.delete_vpc(project_id, service_account_json, network_name)})


@app.route('/gcp-test/subnet/list', methods=['GET'])
async def gcp_subnet_list():
    network_name = "test-vpc"
    region = "us-east4"
    return jsonify({'status': '200', 'message': gcp_network.list_subnet(project_id, service_account_json, network_name, region)})


@app.route('/gcp-test/subnet/create/<subnet_name>', methods=['GET'])
async def gcp_subnet_create(subnet_name):
    network_name = "test-vpc"
    region = "us-east4"
    cidr = "10.0.0.0/16"
    return jsonify({'status': '200', 'message': gcp_network.create_subnet(project_id, service_account_json, network_name, region, subnet_name, cidr)})


@app.route('/gcp-test/zone/list', methods=['GET'])
async def gcp_zone_list():
    return jsonify({'status': '200', 'message': location.get_zones(service_account_json, project_id)})


@app.route('/gcp-test/machine-type/list', methods=['GET'])
async def gcp_machine_type_list():
    zone_name = "us-east1-b"
    return jsonify({'status': '200', 'message': compute.list_machine_type(project_id, service_account_json, zone_name)})

# @app.route('/gcp-test/images/list', methods=['GET'])
# async def gcp_images_type_list():
#     return jsonify({'status': '200', 'message': compute.list_images(project_id,service_account_json)})


@app.route('/gcp-test/instance/create', methods=['GET'])
async def gcp_instance_create():
    vm_name = "test-vm"
    zone_name = "us-east1-b"
    region = "us-east1"
    os_source = "projects/debian-cloud/global/images/family/debian-9"
    # os_source = "rhel-6"
    machine_type = "e2-small"
    network = "default"
    subnet = "default"
    return jsonify({'status': '200', 'message': compute.create_vm(project_id, service_account_json, vm_name, region, zone_name, os_source, machine_type, network, subnet)})
