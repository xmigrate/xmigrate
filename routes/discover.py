from __main__ import app
from utils.dbconn import *
from model.discover import *
import os

@app.route('/discover')
def discover():
    con = create_db_con()
    Post.objects.delete()
    con.close()
    os.popen('ansible-playbook ../ansible/env_setup.yaml > ../logs/ansible/log.txt')
    return jsonify({'status': 'Success'})
