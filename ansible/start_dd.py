import os
from mongoengine import *
import socket
con = connect(host="mongodb://migrationuser:mygrationtool@34.217.74.168:27017/migration?authSource=admin")


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

BluePrint.objects(host=socket.getfqdn('0.0.0.0')).update(status='Started')
os.system('sudo dd if=/dev/xvda bs=64M status=progress | aws s3 cp - s3://migrationdata2/$HOSTNAME.img --sse AES256 --storage-class STANDARD_IA')

BluePrint.objects(host=socket.getfqdn('0.0.0.0')).update(status='Completed')
con.close()
