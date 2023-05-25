from googleapiclient.errors import HttpError
from sqlalchemy import update
from utils.database import *
import os
from model.blueprint import Blueprint
from model.storage import GcpBucket
from model.discover import Discover
from model.disk import Disk
import asyncio
from asyncio.subprocess import PIPE, STDOUT 
from model.project import Project
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
                    if 'error' in result.keys():
                        raise Exception(result['error'])
                    BluePrint.objects(host=host, project=project).update(image_id=result['targetLink'])
                    BluePrint.objects(host=host, project=project).update(status='40')
                    break
                await asyncio.sleep(5)
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
    try:
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
        for host in hosts:
            disks = Discover.objects(project=project,host=host['host']).allow_filtering()[0]['disk_details']
            disk_containers = [] 
            for disk in disks:
                image_name = host['host']+disk['mnt_path'].replace("/","-slash")+'.tar.gz'
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
    finally:
        con.shutdown()


async def start_cloning(project, hostname, db):
    bkt = db.query(GcpBucket).filter(GcpBucket.project==project).first()
    prjct = db.query(Project).filter(Project.name==project).first()
    public_ip = (db.query(Discover).filter(Discover.project==project, Discover.host==hostname).first()).public_ip
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd()

    playbook = "{}/ansible/{}/start_migration.yaml".format(current_dir, prjct.provider)
    inventory = "{}/ansible/projects/{}/hosts".format(current_dir, project)
    extravars = {
        'bucket': bkt.bucket,
        'access_key': bkt.access_key,
        'secret_key': bkt.secret_key,
        'mongodb': mongodb,
        'project': project,
        'ansible_user': prjct.username
    }
    envvars = {
        'ANSIBLE_BECOME_USER': prjct.username,
        'ANSIBLE_LOG_PATH': '{}/logs/ansible/{}/cloning_log.txt'.format(current_dir, project)
    }
    
    cloned = await run_async(playbook=playbook, inventory=inventory, extravars=extravars, envvars=envvars, limit=public_ip, quiet=True)

    if (not (bool(cloned[1].stats['failures']) or bool(cloned[1].stats['dark']))):
        machines = db.query(Blueprint).filter(Blueprint.project==project).all()
        machine_count = db.query(Blueprint).filter(Blueprint.project==project).count()
        flag = True
        status_count = 0
        while flag:
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
        return not flag
    else:
        return False


async def download_worker(osdisk_raw, project, host, db):
    bkt = db.query(GcpBucket).filter(GcpBucket.project==project).first()
    try:
        cur_path = os.getcwd()
        path = f'{cur_path}/projects/{project}/{host}/'

        if not os.path.exists(path):
            os.makedirs(path)

        path += 'disk.raw'
        boto_path = f'{cur_path}/ansible/projects/{project}'

        if not os.path.exists(boto_path):
            os.makedirs(boto_path)

        boto_path += "/.boto"

        if not os.path.exists(boto_path):  
            with open(f'{cur_path}/ansible/gcp/templates/.boto.j') as file_, open(boto_path, "w") as fh:
                template = Template(file_.read())
                rendered_boto = template.render(project_id=bkt.project_id, gs_access_key_id=bkt.access_key, gs_secret_access_key=bkt.secret_key)
                fh.write(rendered_boto)

        if not os.path.exists(path):
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')

            command = f'BOTO_CONFIG={boto_path} gsutil cp gs://{bkt.bucket}/{osdisk_raw} {path}'
            os.popen('echo '+command+'>> ./logs/ansible/migration_log.txt')
            process1 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process1.wait()

            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==host
                ).values(
                status='30'
                ).execution_options(synchronize_session="fetch"))
            db.commit()

            return True
        else:
            return True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==host
            ).values(
            status='-30'
            ).execution_options(synchronize_session="fetch"))
        db.commit()
        
        return False


async def upload_worker(osdisk_raw, project, host, db):
    bkt = db.query(GcpBucket).filter(GcpBucket.project==project).first()
    file_size = '0'
    cur_path = os.getcwd()
    boto_path = f'{cur_path}/ansible/projects/{project}/.boto'

    try:
        osdisk_tar = osdisk_raw.replace(".raw", ".tar.gz")
        tar_path = f'{cur_path}/projects/{project}/{host}/{osdisk_tar}'
        file_size = Path(tar_path).stat().st_size

        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "tar uploading" >> ./logs/ansible/migration_log.txt')

        command = f'BOTO_CONFIG={boto_path} gsutil cp {tar_path} gs://{bkt.bucket}/{osdisk_tar}'
        process3 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()

        os.popen('echo "tar uploaded" >> ./logs/ansible/migration_log.txt')

        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==host
            ).values(
            status='36'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        db.execute(update(Disk).where(
            Disk.project==project and Disk.host==host and Disk.mnt_path==osdisk_raw.split('.raw')[0].split('-')[-1]
            ).values(
            vhd=osdisk_tar, file_size=str(file_size)
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        return True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")

        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==host
            ).values(
            status='-36'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        os.popen('echo "'+repr(e)+'" >> ./logs/ansible/migration_log.txt')
        return False


async def conversion_worker(osdisk_raw, project, host, db):
    downloaded = await download_worker(osdisk_raw, project, host, db)
    if downloaded:
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==host
            ).values(
            status='32'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        try:
            osdisk_tar = osdisk_raw.replace(".raw", ".tar.gz")
            cur_path = os.getcwd()
            path = f'{cur_path}/projects/{project}/{host}/'
            tar_path = path + osdisk_tar
            print("Start compressing")

            os.popen('echo "start compressing">> ./logs/ansible/migration_log.txt')

            command = f'tar --format=oldgnu -Sczf {tar_path} -C {path} disk.raw'
            process2 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process2.wait()

            uploaded = await upload_worker(osdisk_raw, project, host, db)
            if not uploaded: return False

            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==host
                ).values(
                status='35'
                ).execution_options(synchronize_session="fetch"))
            db.commit()

            logger("Conversion completed "+osdisk_raw, "info")
            return True
        except Exception as e:
            print(str(e))
            
            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==host
                ).values(
                status='-35'
                ).execution_options(synchronize_session="fetch"))
            db.commit()

            logger(str(e),"warning")
            return False
    else:
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==host
            ).values(
            status='-32'
            ).execution_options(synchronize_session="fetch"))
        db.commit()
        logger("Downloading image failed" ,"warning")
        return False


async def start_conversion(project, hostname, db):
    if hostname == "all":
        machines = db.query(Blueprint).filter(Blueprint.project==project).all()
    else:
        machines = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==hostname).all()

    for machine in machines:
        disks = (db.query(Discover).filter(Discover.project==project, Discover.host==machine.host).first()).disk_details

        for disk in disks:
            disk_raw = f'{machine.host}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                conversion_done = await conversion_worker(disk_raw, project, machine.host, db)
                if not conversion_done: return False
            except Exception as e:
                print("Conversion failed for "+disk_raw)
                print(str(e))
                logger("Conversion failed for "+disk_raw,"warning")
                logger("Here is the error: "+str(e),"warning")
                return False
    return True

async def start_downloading(project, hostname, db):
    machines = db.query(Blueprint).filter(Blueprint.project==project).all()
    for machine in machines:
        disks = (db.query(Discover).filter(Discover.project==project, Discover.host==machine.host).first()).disk_details

        for disk in disks:
            disk_raw = f'{machine.host}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                downloaded = await download_worker(disk_raw, project, machine.host, db)
                if not downloaded: return False
            except Exception as e:
                print("Download failed for "+disk_raw)
                print(str(e))
                logger("Download failed for "+disk_raw, "warning")
                logger("Here is the error: "+str(e), "warning")
                return False
    return True