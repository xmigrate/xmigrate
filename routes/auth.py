from quart import jsonify, request
from quart_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from __main__ import app
from pkg.common import user

@app.route('/login', methods=['POST'])
async def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = await request.get_json()
    print(type(data))
    username = data['username']
    password = data['password']
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    valid_user = user.check_user(username,password)
    if not valid_user:
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route('/signup', methods=['POST'])
async def signup():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = await request.get_json()
    username = data['username']
    password = data['password']
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user_added = user.add_user(username,password)
    if user_added:
        return jsonify({"msg":"User added successfully"}), 200
    else:
        return jsonify({"msg":"User addition failed"}), 400


@app.route('/user', methods=['GET'])
@jwt_required
async def username():
    username = get_jwt_identity()
    return jsonify(username=username), 200
