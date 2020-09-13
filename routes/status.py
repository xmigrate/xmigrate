from __main__ import app
from utils.dbconn import *
from model.blueprint import *
import json
from quart import jsonify
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/migration/status')
@jwt_required
def migration_status():
    con = create_db_conn()
    machines = json.loads(BluePrint.objects.to_json())
    con.close()
    return jsonify(machines)
