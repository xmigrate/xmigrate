from __main__ import app
import json
from quart import jsonify

from pkg.gcp import network as gcp_network

#remove this once db integration finished
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