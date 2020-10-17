from __main__ import app
from utils.dbconn import *
from model.blueprint import *
import json
from quart import jsonify,request
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/migration/status')
@jwt_required
async def migration_status():
    if request.method == 'GET':
        project = request.args.get('project')
        con = create_db_con()
        machines = json.loads(BluePrint.objects(project=project).to_json())
        con.close()
        return jsonify(machines)
    else:
        return jsonify({"status":500, "msg": "method not supported"})
