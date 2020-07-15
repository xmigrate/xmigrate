import os
from mongoengine import *
import socket
from dotenv import load_dotenv
from os import getenv
import sys

load_dotenv()

db_con_string = getenv("MONGO_DB")

con = connect(host=db_con_string)
storage_accnt = sys.argv[1]
access_key = sys.argv[2]

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

BluePrint.objects(host=socket.getfqdn('0.0.0.0')).update(status='Started cloning')
os.system('sudo dd if=/dev/xvda bs=1M status=progress | azbak - /osdisks/$HOSTNAME.raw --storage-account '+storage_accnt+' --access-key '+access_key)

BluePrint.objects(host=socket.getfqdn('0.0.0.0')).update(status='Completed cloning')
con.close()
