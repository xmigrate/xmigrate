import os
import requests
import json
import sys


bucket = sys.argv[1]
access_key = sys.argv[2]
secret_key = sys.argv[3]
server_con_string = sys.argv[4]
project = sys.argv[5]
hostname = sys.argv[6]
token = sys.argv[7]

def getDisks(project, headers):
    url = server_con_string+"/master/disks/get/" + project
    req = requests.get(url, headers=headers)
    return json.loads(req.text)

headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + token
    }

server_url = server_con_string + "/master/status/update"

def update(status=None, disk_clone=None, mountpoint=None, host=hostname, project=project, url=server_url, headers=headers):

    payload = {
        "table": "Disk",
        "host": host,
        "project": project,
        "status": status,
        "disk_clone": disk_clone,
        "mountpoint": mountpoint
    }
    
    return requests.post(url, data=json.dumps(payload), headers=headers)

diskData = getDisks(project=project, headers=headers)
disks = diskData['data']

update(status=22)

output=''
disk_clone_data = []

try:
    for disk in disks:
        try:
            mnt_path = (disk['mnt_path']).replace("/", "-slash")
            mountpoint = mnt_path.replace("-", "")
            current_disk = {"dev":disk['dev'], "status": "10"}
            disk_clone_data.append(current_disk)
            update(disk_clone=disk_clone_data, mountpoint=mountpoint)

            try:
                output = os.popen('sudo dd if='+disk["dev"]+' bs=4M status=progress | sudo BOTO_CONFIG=/root/.boto /usr/local/bin/gsutil cp - gs://'+bucket+'/'+hostname+mnt_path+'.raw').read()
            except Exception as e:
                print("Incorrect gsutil path trying /usr/local/bin/gsutil")
                output = os.popen('sudo dd if='+disk["dev"]+' bs=4M status=progress | sudo BOTO_CONFIG=/root/.boto /usr/local/bin/gsutil cp - gs://'+bucket+'/'+hostname+mnt_path+'.raw').read()
            for i in disk_clone_data:
                if i['dev']==disk['dev']:
                    i['status'] = "100"
                    i['status_msg'] = output

            update(disk_clone=disk_clone_data, mountpoint=mountpoint)
        except Exception as e:
            print(str(e))
            for i in disk_clone_data:
                if i['dev']==disk['dev']:
                    i['status'] = "-1"
                    i['status_msg'] = output

            update(disk_clone=disk_clone_data, mountpoint=mountpoint)
    update(status=25)
except:  
    update(status=-25)

