from .gcp import get_service_compute_v1
from model.blueprint import Blueprint
from model.discover import Discover
from model.disk import Disk
from model.project import Project
from model.storage import GcpBucket
from utils.logger import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import os
from googleapiclient.errors import HttpError
from jinja2 import Template
from pathlib import Path
from sqlalchemy import update


async def start_image_creation_worker(project, disk_containers, host, db):
    prjct = db.query(Project).filter(Project.name==project).first()

    service = get_service_compute_v1(prjct.service_account)

    for disk in disk_containers:
        if disk['os_disk']:
            disk_body = {
                "name": host.replace('.', '-'),
                "description": "Disks migrated using xmigrate",
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
                    prjct.location
                ]
            }
            
            request = service.images().insert(project=prjct.gcp_project_id, body=disk_body)

            try:
                response = request.execute()
                print(response)
            except HttpError as e:
                if e.resp.status == 409:
                    print("image already created")

                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host
                        ).values(
                        image_id=f"projects/{prjct.gcp_project_id}/global/images/{host.replace('.', '-')}"
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    continue

            while True:
                result = service.globalOperations().get(project=prjct.gcp_project_id, operation=response['name']).execute()
                print(result)

                if result['status'] == 'DONE':
                    print("done.")

                    if 'error' in result.keys():
                        raise Exception(result['error'])
                    
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host
                        ).values(
                        image_id=result['targetLink'], status='40'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    break
                await asyncio.sleep(10)
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

            request = service.disks().insert(project=prjct.gcp_project_id, zone=f"{prjct.location}-a", body=disk_body)
            try:
                response = request.execute()
                print(response)

            except HttpError as e:
                if e.resp.status == 409:
                    print("disk already created")
                    continue
                else:
                    print(str(e))

            while True:
                result = service.zoneOperations().get(project=prjct.gcp_project_id, zone=prjct.location+'-a', operation=response['name']).execute()
                print(result)

                if result['status'] == 'DONE':
                    print("done.")
                    if 'error' in result:
                        raise Exception(result['error'])
                    
                    db.execute(update(Disk).where(
                        Disk.project==project and Disk.host==host and Disk.mnt_path==disk["mnt_path"]
                        ).values(
                        disk_id=result['targetLink']
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host
                        ).values(
                        status='42'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    break
                await asyncio.sleep(10)

async def start_image_creation(project, hostname, db):
    bucket_name = ''
    hosts = []
    try:
        bucket = db.query(GcpBucket).filter(GcpBucket.project==project).first()

        if hostname == "all":
            hosts = db.query(Blueprint).filter(Blueprint.project==project).all()
        else:
            hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.host==hostname).all()

        bucket_name = bucket.bucket
    
        for host in hosts:
            disks = (db.query(Discover).filter(Discover.project==project, Discover.host==host.host).first()).disk_details
            disk_containers = [] 

            for disk in disks:
                image_name = f'{host.host}{disk["mnt_path"].replace("/","-slash")}.tar.gz'
                os_disk = True if disk['mnt_path'] in ['/', '/boot'] else False
                disk_containers.append(
                    {
                        'image_path': f'https://storage.googleapis.com/{bucket_name}/{image_name}',
                        'os_disk': os_disk,
                        'disk_size': disk['disk_size'],
                        'mnt_path': disk['mnt_path'].replace('/','slash')
                    }
                )
            image_created = await start_image_creation_worker(project, disk_containers, host.host, db)
            if not image_created: return False
        return True
    except Exception as e:
        print(repr(e))
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