from __main__ import app
import os
from quart import jsonify, request
from pkg.azure import location
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/locations/get', methods=['POST'])
@jwt_required
async def locations_get():
    if request.method == 'POST':
        data = await request.get_json()
        provider = data['provider']
        if provider == 'azure':
            subscription_id,client_id,secret,tenant_id = data['subscription_id'], data['client_id'], data['secret'], data['tenant_id']
            locations, flag = location.get_locations(subscription_id,client_id,secret,tenant_id)
            if flag:
                return jsonify({'status': '200', 'locations': locations})
            else:
                return jsonify({'status': '500', 'locations': locations, 'message':"wrong credentials"})

