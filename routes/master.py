from app import app

from quart import jsonify, request
from mongoengine import *

from model.blueprint import *
from model.discover import *
from model.disk import *
from utils.dbconn import create_db_con

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Union



@app.get("/master/status")
async def get_master_status():
    return jsonable_encoder({'status': '200'}), 200

class MasterUpdate(BaseModel):
    data: Union[dict,None] = None
    classType: Union[str,None] = None
    classObj: Union[dict,None] = None


@app.post("/master/status/update")
async def master_status_update(data:MasterUpdate):
    update_data = data.data
    class_type = data.classType
    class_obj = data.classObj
    print(class_obj)
    print(class_obj.get('host'))
    print(class_obj.get('project'))

    con = create_db_con()
    try:
        if class_type == 'BluePrint':
            BluePrint.objects(host=class_obj.get('host'), project=class_obj.get('project')).update(**update_data)
        elif class_type == 'Discover':
            Discover.objects(host=class_obj.get('host'), project=class_obj.get('project')).update(**update_data)
        elif class_type == 'Disk':
            Disk.objects(host=class_obj.get('host'),project=class_obj.get('project'),mnt_path=class_obj.get('mnt_path')).update(**update_data)
    except Exception as e:
        print(e)
        con.shutdown()
        return jsonable_encoder({'status': '500', 'message': str(e)})
    finally:
        con.shutdown()
    return jsonable_encoder({'status': '200'})


@app.get("/master/disks/get/{project}/{hostname}")
async def get_disks(project, hostname):
    con = create_db_con()
    disks = []
    try:
        disks = Discover.objects(host=hostname,project=project)[0]['disk_details']
    except Exception as e:
        print(e)
        con.shutdown()
        return jsonable_encoder({'status': '500', 'message': str(e)})
    con.shutdown()
    return jsonable_encoder({'status': '200','data': disks})


@app.get("/master/blueprint/get/{project}/{hostname}")
async def get_blueprint_api(project, hostname):
    con = create_db_con()
    disks = []
    try:
        disks = BluePrint.objects(host=hostname,project=project)[0]['disk_clone']
    except Exception as e:
        print(e)
        con.shutdown()
        return jsonable_encoder({'status': '500', 'message': str(e)})
    con.shutdown()
    return jsonable_encoder({'status': '200','data': disks})
