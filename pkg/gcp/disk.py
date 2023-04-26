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
from ansible_runner import run_async


async def start_image_creation_worker(project, disk_containers, host):
    con = create_db_con()
    location = Project.objects(name=project).allow_filtering()[0]['location']
    project_id = Project.objects(name=project).allow_filtering()[0]['gcp_project_id']
    service_account = Project.objects(name=project).allow_filtering()[0]['service_account']
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
                    Disk.objects(host=host, project=project, mnt_path=disk["mnt_path"]).update(disk_id=result['targetLink'])
                    BluePrint.objects(host=host, project=project).update(status='42')
                    break
                await asyncio.sleep(1)

async def start_image_creation(project, hostname):
   con = create_db_con()
   bucket_name = ''
   hosts = []
   try:
      bucket = GcpBucket.objects(project=project).allow_filtering()[0]
      if hostname == "all":
         hosts = BluePrint.objects(project=project).allow_filtering()
      else:
         hosts = BluePrint.objects(project=project,host=hostname).allow_filtering()
      bucket_name = bucket['bucket']
   except Exception as e:
      print(repr(e))
   finally:
      con.shutdown()
   for host in hosts:
      disks = Discover.objects(project=project,host=host['host']).allow_filtering()[0]['disk_details']
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
        bucket = GcpBucket.objects(project=project).allow_filtering()[0]['bucket']
        accesskey = GcpBucket.objects(project=project).allow_filtering()[0]['access_key']
        secret_key = GcpBucket.objects(project=project).allow_filtering()[0]['secret_key']
        public_ip = Discover.objects(project=project,host=hostname).allow_filtering()[0]['public_ip']
        provider = Project.objects(name=project).allow_filtering()[0]['provider']
        user = Project.objects(name=project).allow_filtering()[0]['username']
    except Exception as e:
        print("Error occurred: "+str(e))
    load_dotenv()
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd()

    playbook = "{}/ansible/{}/start_migration.yaml".format(current_dir, provider)
    inventory = "{}/ansible/projects/{}/hosts".format(current_dir, project)
    extravars = {
        'bucket': bucket,
        'access_key': accesskey,
        'secret_key': secret_key,
        'mongodb': mongodb,
        'project': project,
        'ansible_user': user
    }
    envvars = {
        'ANSIBLE_BECOME_USER': user,
        'ANSIBLE_LOG_PATH': '{}/logs/ansible/{}/cloning_log.txt'.format(current_dir ,project)
    }
    
    await run_async(playbook=playbook, inventory=inventory, extravars=extravars, envvars=envvars, limit=public_ip, quiet=True)

    machines = BluePrint.objects(project=project).allow_filtering()
    machine_count = len(machines)
    flag = True
    status_count = 0
    while flag:
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
    con.shutdown()
    return not flag


async def download_worker(osdisk_raw,project,host):
    con = create_db_con()
    bucket = GcpBucket.objects(project=project).allow_filtering()[0]['bucket']
    secret_key = GcpBucket.objects(project=project).allow_filtering()[0]['secret_key']
    access_key = GcpBucket.objects(project=project).allow_filtering()[0]['access_key']
    project_id = GcpBucket.objects(project=project).allow_filtering()[0]['project_id']
    try:
        cur_path = os.getcwd()
        path = f'{cur_path}/projects/{project}/{host}/osdisks/'
        if not os.path.exists(path):
            os.makedirs(path)
        path += osdisk_raw
        boto_path = cur_path+"/ansible/projects/"+project
        if not os.path.exists(boto_path):
            os.makedirs(boto_path)
        boto_path += "/.boto"
        if not os.path.exists(boto_path):  
            with open(cur_path+"/ansible/gcp/templates/.boto.j2") as file_:
                template = Template(file_.read())
            rendered_boto = template.render(project_id=project_id, gs_access_key_id=access_key, gs_secret_access_key=secret_key)
            with open(boto_path, "w") as fh:
                fh.write(rendered_boto)
        if not os.path.exists(path):
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')
            command = 'BOTO_CONFIG='+boto_path +' gsutil cp gs://'+bucket+'/'+osdisk_raw + ' ' +path
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
        con.shutdown()


async def upload_worker(osdisk_raw,project,host):
    con = create_db_con()
    bucket = GcpBucket.objects(project=project).allow_filtering()[0]['bucket']
    secret_key = GcpBucket.objects(project=project).allow_filtering()[0]['secret_key']
    access_key = GcpBucket.objects(project=project).allow_filtering()[0]['access_key']
    project_id = GcpBucket.objects(project=project).allow_filtering()[0]['project_id']
    pipe_result = ''
    file_size = '0'
    cur_path = os.getcwd()
    boto_path = cur_path+"/ansible/projects/"+project+"/.boto"
    try:
        osdisk_tar = osdisk_raw.replace(".raw",".tar.gz")
        tar_path = f'{cur_path}/projects/{project}/{host}/osdisks/{osdisk_tar}'
        file_size = Path(tar_path).stat().st_size 
        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "tar uploading" >> ./logs/ansible/migration_log.txt')
        command = 'BOTO_CONFIG='+boto_path +' gsutil cp ' + tar_path+ ' gs://'+bucket+'/'+osdisk_tar
        process3 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()
        os.popen('echo "tar uploaded" >> ./logs/ansible/migration_log.txt')
        BluePrint.objects(project=project,host=host).update(status='36')
        Disk.objects(host=host,project=project,mnt_path=osdisk_raw.split('.raw')[0].split('-')[-1]).update(vhd=osdisk_tar, file_size=str(file_size))
        return True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        BluePrint.objects(project=project,host=host).update(status='-36')
        os.popen('echo "'+repr(e)+'" >> ./logs/ansible/migration_log.txt')
        return False
    finally:
        con.shutdown()


async def conversion_worker(osdisk_raw,project,host):
    try:
        con = create_db_con()
        downloaded = await download_worker(osdisk_raw,project,host)
        if downloaded:
            BluePrint.objects(project=project,host=host).update(status='32')
            try:
                osdisk_tar = osdisk_raw.replace(".raw",".tar.gz")
                cur_path = os.getcwd()
                path = f'{cur_path}/projects/{project}/{host}/osdisks/'
                tar_path = path + osdisk_tar
                print("Start compressing")
                os.popen('echo "start compressing">> ./logs/ansible/migration_log.txt')
                command = "tar --format=oldgnu -Sczf "+ tar_path+" "+ path + osdisk_raw
                process2 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
                await process2.wait()
                uploaded = await upload_worker(osdisk_raw,project,host)
                if not uploaded:
                    return False
                BluePrint.objects(project=project,host=host).update(status='35')
                logger("Conversion completed "+osdisk_raw,"warning")
                return True
            except Exception as e:
                print(str(e))
                BluePrint.objects(project=project,host=host).update(status='-35')
                logger(str(e),"warning")
                return False
        else:
            BluePrint.objects(project=project,host=host).update(status='-32')
            logger("Downloading image failed","warning")
            return False
    finally:
        con.shutdown()


async def start_conversion(project,hostname):
    con = create_db_con()
    if Project.objects(name=project).allow_filtering()[0]['provider'] == "gcp":
        if hostname == "all":
            machines = BluePrint.objects(project=project).allow_filtering()
        else:
            machines = BluePrint.objects(project=project, host=hostname).allow_filtering()
        for machine in machines:
            disks = Discover.objects(project=project, host=machine['host']).allow_filtering()[0]['disk_details']
            for disk in disks:
                disk_raw = machine['host']+disk['mnt_path'].replace('/','-slash')+".raw"
                try:
                    conversion_done = await conversion_worker(disk_raw,project,machine['host'])
                    if not conversion_done:
                        return False
                except Exception as e:
                    print("Conversion failed for "+disk_raw)
                    print(str(e))
                    logger("Conversion failed for "+disk_raw,"warning")
                    logger("Here is the error: "+str(e),"warning")
                    return False
        con.shutdown()
        return True

async def start_downloading(project,hostname):
    con = create_db_con()
    if Project.objects(name=project).allow_filtering()[0]['provider'] == "gcp":
        machines = BluePrint.objects(project=project).allow_filtering()
        for machine in machines:
            disks = Discover.objects(project=project, host=machine['host']).allow_filtering()[0]['disk_details']
            for disk in disks:
                disk_raw = machine['host']+disk['mnt_path'].replace('/','-slash')+".raw"
                try:
                    await download_worker(disk_raw,project,machine['host'])  
                except Exception as e:
                    print("Download failed for "+disk_raw)
                    print(str(e))
                    logger("Download failed for "+disk_raw,"warning")
                    logger("Here is the error: "+str(e),"warning")
                    return False
        con.shutdown()
        return True