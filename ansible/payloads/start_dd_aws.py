import os
from mongoengine import *
import socket
from dotenv import load_dotenv
from os import getenv

load_dotenv()

db_con_string = getenv("MONGO_DB")

con = connect(host=db_con_string)
bucket = getenv("BUCKET")

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

BluePrint.objects(host=socket.getfqdn('0.0.0.0')).update(status='10')
os.system('sudo dd if=/dev/xvda bs=1M status=progress | aws s3 cp - s3://'+bucket+'/$HOSTNAME.img --sse AES256 --storage-class STANDARD_IA')

BluePrint.objects(host=socket.getfqdn('0.0.0.0')).update(status='25')
con.close()
