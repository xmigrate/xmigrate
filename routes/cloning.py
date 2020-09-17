from __main__ import app
import os
from quart_jwt_extended import jwt_required, get_jwt_identity

@app.route('/start/cloning', methods=['POST','GET'])
@jwt_required
def start_migration():
    os.popen('ansible-playbook ../ansible/start_migration.yaml > ../ansible/migration_log.txt')
    return jsonify({'status': 'Success'})
