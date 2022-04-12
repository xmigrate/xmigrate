import os
import requests
import json
import socket
import sys


db_con_string = sys.argv[3]
server_con_string = sys.argv[3]
url = sys.argv[1]
sas = sys.argv[2]
project = sys.argv[4]
hostname = sys.argv[5]

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
    host = str()
    ip = str()
    subnet = str()
    network = str()
    ports = list()
    cores = str()
    cpu_model = str()
    ram = str()
    disk_details = list()
    project = str()
    public_ip = str()
    meta = {
        'indexes': [
            {'fields': ('host', 'project'), 'unique': True}
        ]
    }


class BluePrint(Document):
    host = str()
    ip = str()
    subnet = str()
    network = str()
    ports = list()
    cores = str()
    cpu_model = str()
    ram = str()
    machine_type = str()
    status = str()
    image_id = str()
    vpc_id = str()
    subnet_id = str()
    public_route = bool()
    ig_id = str()
    route_table = str()
    vm_id = str()
    project = str()
    nic_id = str()
    disk_clone = list()
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
            output = os.popen('sudo dd if='+disk["dev"]+' bs=1M status=progress | azcopy copy "'+url+hostname+mnt_path+'.raw?'+sas+'" --from-to PipeBlob').read()
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
