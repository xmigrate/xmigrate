from email.mime import image
from googleapiclient.errors import HttpError
from utils.dbconn import *
import os
from model.blueprint import *
from model.storage import *
from model.discover import *
from model.disk import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT 
from model.discover import *
from model.project import *
from .gcp import get_service_compute_v1
from utils.logger import *
from jinja2 import Template
from pathlib import Path



async def start_image_creation_worker(project, disk_containers, host):
    con = create_db_con()
    location = Project.objects(name=project)[0]['location']
    project_id = Project.objects(name=project)[0]['gcp_project_id']
    service_account = Project.objects(name=project)[0]['service_account']
    service = get_service_compute_v1(service_account)
    for disk in disk_containers:
        if disk['os_disk']:
            disk_body = {
                "name": host.replace('.','-'),
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
                project=project_id, body=disk_body)
            try:
                response = request.execute()
                print(response)
            except HttpError as e:
                if e.resp.status == 409:
                    print("image already created")
                    BluePrint.objects(host=host, project=project).update(image_id='projects/'+project_id+'/global/images/'+host.replace('.','-'))
                    continue
            while True:
                result = service.globalOperations().get(project=project_id, operation=response['name']).execute()
                print(result)
                if result['status'] == 'DONE':
                    print("done.")
                    if 'error' in result:
                        raise Exception(result['error'])
                    BluePrint.objects(host=host, project=project).update(image_id=result['targetLink'])
                    BluePrint.objects(host=host, project=project).update(status='40')
                    break
                await asyncio.sleep(1)
        else:
            disk_body = {
                "name": host.replace('.','-')+"-"+disk["mnt_path"],
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
            try:
                response = request.execute()
                print(response)
            except HttpError as e:
                if e.resp.status == 409:
                    print("disk already created")
                    continue
                else:
                    print(e)
            while True:
                result = service.zoneOperations().get(project=project_id, zone=location+'-a', operation=response['name']).execute()
                print(result)
                if result['status'] == 'DONE':
                    print("done.")
                    if 'error' in result:
                        raise Exception(result['error'])
                    Disk.objects(host=host, project=project, vhd=disk['image_path'].split('/')[-1]).update(disk_id=result['targetLink'])
                    BluePrint.objects(host=host, project=project).update(status='42')
                    break
                await asyncio.sleep(1)

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
                'disk_size': disk['disk_size'],
                'mnt_path': disk['mnt_path'].replace('/','slash')
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
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd()
    if hostname == "all":
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/gcp/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\""
    else:
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/gcp/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\" --limit "+public_ip+" --user "+user+" --become-user "+user+" --become-method sudo"
    print(command)
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


async def download_worker(osdisk_raw,project,host):
    con = create_db_con()
    bucket = GcpBucket.objects(project=project)[0]['bucket']
    secret_key = GcpBucket.objects(project=project)[0]['secret_key']
    access_key = GcpBucket.objects(project=project)[0]['access_key']
    project_id = GcpBucket.objects(project=project)[0]['project_id']
    
    try:
        cur_path = os.getcwd()
        path = cur_path+"/osdisks/"+osdisk_raw.replace('.raw','')+"/disk.raw"

        boto_path = cur_path+"/ansible/"+project+"/.boto"
        if not os.path.exists(boto_path):
            with open(cur_path+"/ansible/"+"gcp/templates/.boto.j2") as file_:
                template = Template(file_.read())
            rendered_boto = template.render(project_id=project_id, gs_access_key_id=access_key, gs_secret_access_key=secret_key)
            with open(boto_path, "w") as fh:
                fh.write(rendered_boto)
        if not os.path.exists(path):
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')
            command = 'BOTO_CONFIG='+boto_path +' gsutil cp gs://'+bucket+'/'+osdisk_raw + ' ' +path
            print(command)
            os.popen('echo '+command+'>> ./logs/ansible/migration_log.txt')
            process1 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process1.wait()
            BluePrint.objects(project=project,host=host).update(status='30')
            return True
        else:
            return True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        BluePrint.objects(project=project,host=host).update(status='-30')
        return False
    finally:
        con.close()


async def upload_worker(osdisk_raw,project,host):
    con = create_db_con()
    bucket = GcpBucket.objects(project=project)[0]['bucket']
    secret_key = GcpBucket.objects(project=project)[0]['secret_key']
    access_key = GcpBucket.objects(project=project)[0]['access_key']
    project_id = GcpBucket.objects(project=project)[0]['project_id']
    pipe_result = ''
    file_size = '0'
    cur_path = os.getcwd()
    boto_path = cur_path+"/ansible/"+project+"/.boto"
    try:
        osdisk_tar = osdisk_raw.replace(".raw",".tar.gz")
        tar_path = cur_path+"/osdisks/"+osdisk_raw.replace('.raw','')+"/"+osdisk_tar
        file_size = Path(tar_path).stat().st_size 
        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "tar uploading" >> ./logs/ansible/migration_log.txt')
        command = 'BOTO_CONFIG='+boto_path +' gsutil cp ' + tar_path+ ' gs://'+bucket+'/'+osdisk_tar
        process3 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()
        os.popen('echo "tar uploaded" >> ./logs/ansible/migration_log.txt')
        BluePrint.objects(project=project,host=host).update(status='36')
        Disk.objects(host=host,project=project,mnt_path=osdisk_raw.split('.raw')[0].split('-')[-1]).update_one(vhd=osdisk_tar, file_size=str(file_size), upsert=True)
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        BluePrint.objects(project=project,host=host).update(status='-36')
        os.popen('echo "'+repr(e)+'" >> ./logs/ansible/migration_log.txt')
    finally:
        con.close()


async def conversion_worker(osdisk_raw,project,host):
    downloaded = await download_worker(osdisk_raw,project,host)
    if downloaded:
        con = create_db_con()
        BluePrint.objects(project=project,host=host).update(status='32')        
        try:
            osdisk_tar = osdisk_raw.replace(".raw",".tar.gz")
            cur_path = os.getcwd()
            path = cur_path+"/osdisks/"+osdisk_raw.replace('.raw','')
            tar_path = cur_path+"/osdisks/"+osdisk_raw.replace('.raw','')+"/"+osdisk_tar
            print("Start compressing")
            print(path)
            os.popen('echo "start compressing">> ./logs/ansible/migration_log.txt')
            command = "tar --format=oldgnu -Sczf "+ tar_path+" -C "+path+" disk.raw"
            process2 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process2.wait()
            await upload_worker(osdisk_raw,project,host)
            BluePrint.objects(project=project,host=host).update(status='35')
            logger("Conversion completed "+osdisk_raw,"warning")
        except Exception as e:
            print(str(e))
            BluePrint.objects(project=project,host=host).update(status='-35')
            logger(str(e),"warning")
    else:
        BluePrint.objects(project=project,host=host).update(status='-32')
        logger("Downloading image failed","warning")
    con.close()


async def start_conversion(project,hostname):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "gcp":
        if hostname == "all":
            machines = BluePrint.objects(project=project)
        else:
            machines = BluePrint.objects(project=project, host=hostname)
        for machine in machines:
            disks = Discover.objects(project=project, host=machine['host'])[0]['disk_details']
            for disk in disks:
                disk_raw = machine['host']+disk['mnt_path'].replace('/','-slash')+".raw"
                print(disk_raw)
                try:
                    await conversion_worker(disk_raw,project,machine['host'])  
                except Exception as e:
                    print("Conversion failed for "+disk_raw)
                    print(str(e))
                    logger("Conversion failed for "+disk_raw,"warning")
                    logger("Here is the error: "+str(e),"warning")
                    return False
        con.close()
        return True

async def start_downloading(project,hostname):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "gcp":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            disks = Discover.objects(project=project, host=machine['host'])[0]['disk_details']
            for disk in disks:
                disk_raw = machine['host']+disk['mnt_path'].replace('/','-slash')+".raw"
                print(disk_raw)
                try:
                    await download_worker(disk_raw,project,machine['host'])  
                except Exception as e:
                    print("Download failed for "+disk_raw)
                    print(str(e))
                    logger("Download failed for "+disk_raw,"warning")
                    logger("Here is the error: "+str(e),"warning")
                    return False
        con.close()
        return True