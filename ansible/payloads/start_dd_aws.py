import os
from mongoengine import *
import socket
import sys

db_con_string = sys.argv[4]
con = connect(host=db_con_string)
bucket = sys.argv[1]
access_key = sys.argv[2]
secret_key = sys.argv[3]
project = sys.argv[5]

hostname = socket.gethostname()

class BluePrint(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True, unique=True)
    subnet = StringField(required=True, max_length=50)
    network = StringField(required=True, max_length=50)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=50)
    machine_type = StringField(required=True, max_length=150)
    status = StringField(required=False, max_length=100)
    ami_id = StringField(required=False, max_length=100)
    project = StringField(required=True, max_length=50)
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }

BluePrint.objects(host=hostname,project=project).update(status='10')
try:
    os.system('sudo dd if=/dev/xvda bs=1M status=progress | aws s3 cp - s3://'+bucket+'/$HOSTNAME.img --sse AES256 --storage-class STANDARD_IA --profile '+project)
    BluePrint.objects(host=hostname, project=project).update(status='25')
except:
    BluePrint.objects(host=hostname, project=project).update(status='-25')
finally:
    con.close()
