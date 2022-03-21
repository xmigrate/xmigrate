from __main__ import app

from quart import jsonify, request
from mongoengine import *

from model.blueprint import *
from model.discover import *
from utils.dbconn import create_db_con


@app.route("/master/status", methods=['GET'])
async def get_master_status():
    return jsonify({'status': '200'}), 200


@app.route("/master/status/update", methods=['POST'])
async def master_status_update():
    data = await request.get_json()
    update_data = data['data']
    class_type = data['classType']
    class_obj = data['classObj']
    print(class_obj)
    print(class_obj.get('host'))
    print(class_obj.get('project'))

    con = create_db_con()
    try:
        if class_type == 'BluePrint':
            BluePrint.objects(host=class_obj.get('host'), project=class_obj.get('project')).update(**update_data)
        elif class_type == 'Discover':
            Discover.objects(host=class_obj.get('host'), project=class_obj.get('project')).update(**update_data)
    except Exception as e:
        print(e)
        con.close()
        return jsonify({'status': '500', 'message': str(e)}), 500
    finally:
        con.close()
    return jsonify({'status': '200'}), 200
