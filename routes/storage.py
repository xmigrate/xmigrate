from app import app
import os
from quart import jsonify, request
from pkg.azure import storage as st
from pkg.aws import bucket as bk
from pkg.gcp import bucket as gbk
from quart_jwt_extended import jwt_required, get_jwt_identity


@app.route('/storage/create', methods=['POST'])
@jwt_required
async def storage_create():
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        project = data['project']
        if provider == 'azure':
            storage = data['storage']
            container = data['container']
            access_key = data['access_key']
            storage_created = st.create_storage(
                project, storage, container, access_key)
        elif provider == 'aws':
            bucket = data['bucket']
            secret_key = data['secret_key']
            access_key = data['access_key']
            storage_created = bk.create_bucket(
                project, bucket, secret_key, access_key)
        elif provider == 'gcp':
            bucket = data['bucket']
            secret_key = data['secret_key']
            access_key = data['access_key']
            storage_created = gbk.create_bucket(project, bucket, access_key,secret_key)
        if storage_created:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})


@app.route('/storage/get', methods=['GET'])
@jwt_required
async def storage_get():
    if request.method == 'GET':
        name = request.args.get('project')
        provider = request.args.get('provider')
        if provider == "azure":
            return jsonify(st.get_storage(name))
        elif provider == "aws":
            return jsonify(bk.get_storage(name))
        elif provider == "gcp":
            return jsonify(gbk.get_storage(name))


@app.route('/storage/update', methods=['POST'])
@jwt_required
async def storage_update():
    if request.method == 'POST':
        data = await request.get_json()
        project = data['project']
        provider = data['provider']
        if provider == 'azure':
            storage = data['storage']
            container = data['container']
            access_key = data['access_key']
            storage_updated = st.update_storage(
                project, storage, container, access_key)
        elif provider == "aws":
            bucket = data['bucket']
            secret_key = data['secret_key']
            access_key = data['access_key']
            storage_updated = bk.update_bucket(
                project, bucket, secret_key, access_key)
        elif provider == 'gcp':
            bucket = data['bucket']
            secret_key = data['secret_key']
            access_key = data['access_key']
            storage_updated = gbk.update_bucket(
                project, bucket, access_key,secret_key)
        if storage_updated:
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '500'})
