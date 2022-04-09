import os
import requests
import json
from mongoengine import StringField
from mongoengine import ListField
from collections import OrderedDict
import socket
import sys

db_con_string = sys.argv[4]
server_con_string = sys.argv[4]
bucket = sys.argv[1]
access_key = sys.argv[2]
secret_key = sys.argv[3]
project = sys.argv[5]

hostname = socket.gethostname()

class Document():
    def __init__(self, *args, **values):
        print(self)

    @classmethod
    def objects(self, **values):
        for key in values:
            setattr(self, key, values[key])
        return self

    @classmethod
    def update(self, **kwargs):
        url = server_con_string+"/master/status/update"
        jsonObj = {}
        for i in dir(self):
            if i.startswith('_'):
                continue
            jsonObj[i] = getattr(self, i)
            if(str(getattr(self, i)).startswith('<')):
                jsonObj[i] = None    
        data = {
            'classObj': jsonObj,
            'classType': self.__name__,
            'data': kwargs
        }
        headers = {'Accept-Encoding': 'UTF-8', 'Content-Type': 'application/json', 'Accept': '*/*'}
        req = requests.post(url, data=json.dumps(data),headers=headers)
        print(req.text)
        return self

def getDisks(project, hostname):
    url = server_con_string+"/master/disks/get/" + project + "/" + hostname
    req = requests.get(url)
    return json.loads(req.text)

class Discover(Document):
    host = StringField(required=True, max_length=200 )
    ip = StringField(required=True)
    subnet = StringField(required=True, max_length=150)
    network = StringField(required=True, max_length=150)
    ports = ListField()
    cores = StringField(max_length=2)
    cpu_model = StringField(required=True, max_length=150)
    ram = StringField(required=True, max_length=150)
    disk_details = ListField()
    project = StringField(required=True, max_length=150)
    public_ip = StringField(required=True, max_length=150)
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }

class BluePrint(Document):
    host = StringField(required=True, max_length=200, unique=True)
    ip = StringField(required=True)
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
    disk_clone = ListField()
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }

diskData = getDisks(project=project, hostname=hostname)
disks = diskData['data']
BluePrint.objects(host=hostname,project=project).update(status='22')

output=''
disk_clone_data = []

try:
    for disk in disks:
        try:
            current_disk = {"dev":disk['dev'], "status":"10"}
            disk_clone_data.append(current_disk)
            BluePrint.objects(host=hostname,project=project).update(disk_clone=disk_clone_data)
            mnt_path = disk['mnt_path']
            mnt_path = mnt_path.replace("/","-slash")
            output = os.popen('sudo dd if='+disk["dev"]+' bs=4M status=progress | BOTO_CONFIG=/root/.boto /usr/local/bin/gsutil cp - gs://'+bucket+'/'+hostname+mnt_path+'.raw').read()
            for i in disk_clone_data:
                if i['dev']==disk['dev']:
                    i['status'] = "100"
                    i['status_msg'] = output
            BluePrint.objects(host=hostname,project=project).update(disk_clone=disk_clone_data)
        except Exception as e:
            print(str(e))
            for i in disk_clone_data:
                if i['dev']==disk['dev']:
                    i['status'] = "-1"
                    i['status_msg'] = output
            BluePrint.objects(host=hostname,project=project).update(disk_clone=disk_clone_data)
    BluePrint.objects(host=hostname, project=project).update(status='25')
except:  
    BluePrint.objects(host=hostname, project=project).update(status='-25')

