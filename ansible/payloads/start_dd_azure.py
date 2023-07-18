import os
import requests
import json
import sys


url = sys.argv[1]
sas = sys.argv[2]
server_con_string = sys.argv[3]
project = sys.argv[4]
hostname = sys.argv[5]
token = sys.argv[6]

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
            current_disk = {"dev": disk['dev'], "status": "10"}
            disk_clone_data.append(current_disk)
            update(disk_clone=disk_clone_data, mountpoint=mountpoint)

            output = os.popen('sudo dd if='+disk["dev"]+' bs=1M status=progress | azcopy copy "'+url+hostname+mnt_path+'.raw?'+sas+'" --from-to PipeBlob').read()
            for i in disk_clone_data:
                if i['dev'] == disk['dev']:
                    i['status'] = "100"
                    i['status_msg'] = output

            update(disk_clone=disk_clone_data, mountpoint=mountpoint)
        except Exception as e:
            print(str(e))
            for i in disk_clone_data:
                if i['dev'] == disk['dev']:
                    i['status'] = "-1"
                    i['status_msg'] = output
                    
            update(disk_clone=disk_clone_data, mountpoint=mountpoint)
    update(status=25)
except:  
    update(status=-25)
