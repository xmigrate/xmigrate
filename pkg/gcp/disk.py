from email.mime import image
from utils.dbconn import *
import os
from model.blueprint import *
from model.storage import *
from model.discover import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT 
from model.discover import *
from model.project import *
from .gcp import get_service_compute_v1

async def start_image_creation_worker(project, disk_containers, host):
    con = create_db_con()
    location = Project.objects(name=project)[0]['location']
    project_id = Project.objects(name=project)[0]['project_id']
    service_account = Project.objects(name=project)[0]['service_account']
    service = get_service_compute_v1(service_account)
    for disk in disk_containers:
        if disk['os_disk']:
            disk_body = {
                "name": host,
                "description": "Disk's migrated using xmigrate",
                "rawDisk": {
                    "source": disk['image_path']
                },
                
                # "archiveSizeBytes": string,
                # "diskSizeGb": str(disk['disk_size']),
                # "family": string,
                
                "labels": {
                    "app": "xmigrate",  
                },
            
                "storageLocations": [
                    location
                ]
                }
            request = service.images().insert(
                project=project_id, zone=location+'-a', body=disk_body)
            response = request.execute()
        else:
            disk_body = {
                "name": host,
                "description": "Disk's migrated using xmigrate",
                # "sizeGb": string,
                "sourceStorageObject": disk['image_path'],
                # "type": string,
                "labels": {
                    "app": "xmigrate",
                }
                }
            request = service.disks().insert(
                project=project_id, zone=location+'-a', body=disk_body)
            response = request.execute()

async def start_image_creation(project, hostname):
   con = create_db_con()
   bucket_name = ''
   hosts = []
   try:
      bucket = GcpBucket.objects(project=project)[0]
      if hostname == "all":
         hosts = BluePrint.objects(project=project)
      else:
         hosts = BluePrint.objects(project=project,host=hostname)
      bucket_name = bucket['bucket']
   except Exception as e:
      print(repr(e))
   finally:
      con.close()
   for host in hosts:
      disks = Discover.objects(project=project,host=host['host'])[0]['disk_details']
      disk_containers = [] 
      for disk in disks:
         image_name = host['host']+disk['mnt_path'].replace("/","-slash")+'.tar.gz'
         print(image_name)
         os_disk = True if disk['mnt_path'] in ['/', '/boot'] else False
         disk_containers.append(
            {
                'image_path': 'https://storage.googleapis.com/'+bucket_name+'/'+image_name,
                'os_disk': os_disk,
                'disk_size': disk['file_size']
            }
         )
      await start_image_creation_worker(project, disk_containers, host['host'])
   return True


async def start_cloning(project, hostname):
    con = create_db_con()
    try:
        bucket = GcpBucket.objects(project=project)[0]['bucket']
        accesskey = GcpBucket.objects(project=project)[0]['access_key']
        secret_key = GcpBucket.objects(project=project)[0]['secret_key']
        public_ip = Discover.objects(project=project,host=hostname)[0]['public_ip']
        user = Project.objects(name=project)[0]['username']
    except Exception as e:
        print("Error occurred: "+str(e))
    load_dotenv()
    mongodb = os.getenv('MONGO_DB')
    current_dir = os.getcwd()
    print("/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/gcp/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\"")
    if hostname == "all":
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/gcp/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\""
    else:
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/gcp/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\" --limit "+public_ip+" --user "+user+" --become-user "+user+" --become-method sudo"
    process = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
    await process.wait()
    machines = BluePrint.objects(project=project)
    machine_count = len(machines)
    flag = True
    status_count = 0
    while flag:
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
    con.close()
    return not flag

