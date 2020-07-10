from __main__ import app
import os

@app.route('/start/cloning', methods=['POST','GET'])
def start_migration():
    os.popen('ansible-playbook ../ansible/start_migration.yaml > ../ansible/migration_log.txt')
    return jsonify({'status': 'Success'})
