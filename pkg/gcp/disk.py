from .gcp import get_service_compute_v1
from schemas.disk import DiskUpdate
from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.discover import get_discover
from services.disk import get_diskid, update_disk
from services.machines import get_all_machines, get_machine_by_hostname, update_vm
from services.project import get_project_by_name
from services.storage import get_storage
from utils.logger import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import json
import os
from googleapiclient.errors import HttpError
from jinja2 import Template
from pathlib import Path


async def start_image_creation_worker(project, disk_containers, host, db):
    service = get_service_compute_v1(json.loads(project.gcp_service_token))
    gcp_project_id = json.loads(project.gcp_service_token)['project_id']
    try:
        for disk in disk_containers:
            if disk['os_disk']:
                disk_body = {
                    "name": (host.hostname).replace('.', '-'),
                    "description": "Disk migrated using xmigrate",
                    "rawDisk": {
                        "source": disk['image_path']
                    },
                    
                    # "archiveSizeBytes": string,
                    # "diskSizeGb": str(disk['disk_size']),
                    # "family": string,
                    
                    "labels": {"app": "xmigrate",},
                    "storageLocations": [project.location]
                }
                
                request = service.images().insert(project=gcp_project_id, body=disk_body)

                try:
                    response = request.execute()
                    print(response)
                except HttpError as e:
                    if e.resp.status == 409:
                        print("Image already created!")

                        vm_data = VMUpdate(machine_id=host.id, image_id=f"projects/{gcp_project_id}/global/images/{(host.hostname).replace('.', '-')}")
                        update_vm(vm_data, db)
                        continue

                while True:
                    result = service.globalOperations().get(project=gcp_project_id, operation=response['name']).execute()
                    print(result)

                    if result['status'] == 'DONE':
                        print("Task done.")

                        if 'error' in result.keys():
                            raise Exception(result['error'])
                        
                        vm_data = VMUpdate(machine_id=host.id, image_id=result['targetLink'], status='40')
                        update_vm(vm_data, db)
                        break
                    await asyncio.sleep(10)
            else:
                disk_body = {
                    "name": f"{(host.hostname).replace('.', '-')}-{disk['mnt_path']}",
                    "description": "Disk migrated using xmigrate",
                    # "sizeGb": string,
                    "sourceStorageObject": disk['image_path'],
                    # "type": string,
                    "labels": {"app": "xmigrate",}
                }

                request = service.disks().insert(project=gcp_project_id, zone=f"{project.location}-a", body=disk_body)
                try:
                    response = request.execute()
                    print(response)
                except HttpError as e:
                    if e.resp.status == 409:
                        print("Disk already created!")
                        continue
                    else:
                        print(str(e))

                while True:
                    result = service.zoneOperations().get(project=gcp_project_id, zone=f"{project.location}-a", operation=response['name']).execute()
                    print(result)

                    if result['status'] == 'DONE':
                        print("Task done.")
                        if 'error' in result:
                            raise Exception(result['error'])
                        
                        disk_id = get_diskid(host.id, disk['mnt_path'].replace('/', 'slash'), db)
                        disk_data = DiskUpdate(disk_id=disk_id, target_disk_id=result['targetLink'])
                        update_disk(disk_data, db)

                        vm_data = VMUpdate(machine_id=host.id, status='42')
                        update_vm(vm_data, db)
                        break
                    await asyncio.sleep(10)
        return True
    except Exception as e:
        print(str(e))
        return False


async def start_image_creation(user, project, hostname, db) -> bool:
    try:
        project = get_project_by_name(user, project, db)
        storage = get_storage(project.id, db)
        blueprint_id = get_blueprintid(project.id, db)

        if hostname == ["all"]:
            hosts = get_all_machines(blueprint_id, db)
        else:
            hosts = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]
    
        for host in hosts:
            disks = json.loads(get_discover(project.id, db)[0].disk_details)
            disk_containers = [] 

            for disk in disks:
                image_name = f'{host.hostname}{disk["mnt_path"].replace("/","-slash")}.tar.gz'
                os_disk = True if disk['mnt_path'] in ['/', '/boot'] else False
                disk_containers.append(
                    {
                        'image_path': f'https://storage.googleapis.com/{storage.bucket_name}/{image_name}',
                        'os_disk': os_disk,
                        'disk_size': disk['disk_size'],
                        'mnt_path': disk['mnt_path'].replace('/','slash')
                    }
                )
            image_created = await start_image_creation_worker(project, disk_containers, host, db)
            if not image_created: return False
        return True
    except Exception as e:
        print(repr(e))
        return False


async def download_worker(osdisk_raw, project, host, db) -> bool:
    storage = get_storage(project.id, db)
    try:
        cur_path = os.getcwd()
        path = f'{cur_path}/projects/{project.name}/{host.hostname}/'

        if not os.path.exists(path):
            os.makedirs(path)

        path += 'disk.raw'
        boto_path = f'{cur_path}/ansible/projects/{project.name}'

        if not os.path.exists(boto_path):
            os.makedirs(boto_path)

        boto_path += "/.boto"

        if not os.path.exists(boto_path):  
            with open(f'{cur_path}/ansible/gcp/templates/.boto.j2') as file_, open(boto_path, "w") as fh:
                template = Template(file_.read())
                rendered_boto = template.render(project_id=json.loads(project.gcp_service_token)['project_id'], gs_access_key_id=storage.access_key, gs_secret_access_key=storage.secret_key)
                fh.write(rendered_boto)

        if not os.path.exists(path):
            os.popen('echo "download started" > ./logs/ansible/migration_log.txt')

            command = f'BOTO_CONFIG={boto_path} gsutil cp gs://{storage.bucket_name}/{osdisk_raw} {path}'
            os.popen('echo ' + command + ' >> ./logs/ansible/migration_log.txt')
            process1 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process1.wait()

            vm_data = VMUpdate(machine_id=host.id, status=30)
            update_vm(vm_data, db)
            return True
        else:
            return True
    except Exception as e:
        print(str(e))
        logger(str(e), "warning")
        
        vm_data = VMUpdate(machine_id=host.id, status=-30)
        update_vm(vm_data, db)
        return False


async def upload_worker(osdisk_raw, project, disk_mountpoint, host, db) -> bool:
    storage = get_storage(project.id, db)
    file_size = '0'
    cur_path = os.getcwd()
    boto_path = f'{cur_path}/ansible/projects/{project.name}/.boto'

    try:
        osdisk_tar = osdisk_raw.replace(".raw", ".tar.gz")
        tar_path = f'{cur_path}/projects/{project.name}/{host.hostname}/{osdisk_tar}'
        file_size = Path(tar_path).stat().st_size

        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "tar uploading" >> ./logs/ansible/migration_log.txt')

        command = f'BOTO_CONFIG={boto_path} gsutil cp {tar_path} gs://{storage.bucket_name}/{osdisk_tar}'
        process3 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()

        os.popen('echo "tar uploaded" >> ./logs/ansible/migration_log.txt')

        vm_data = VMUpdate(machine_id=host.id, status=32)
        update_vm(vm_data, db)

        disk_id = get_diskid(host.id, disk_mountpoint.replace('/', 'slash'), db)
        disk_data = DiskUpdate(disk_id=disk_id, vhd=osdisk_tar, file_size=str(file_size))
        update_disk(disk_data, db)
        return True
    except Exception as e:
        print(str(e))
        logger(str(e), "warning")

        vm_data = VMUpdate(machine_id=host.id, status=-32)
        update_vm(vm_data, db)

        os.popen('echo "' + str(e)+ '" >> ./logs/ansible/migration_log.txt')
        return False


async def conversion_worker(osdisk_raw, project, disk_mountpoint, host, db) -> bool:
    try:
        await download_worker(osdisk_raw, project, host, db)
    except Exception as e:
        print("Download failed for "+ osdisk_raw + " :" + str(e))
        logger("Download failed for "+ osdisk_raw + " :" + str(e), "warning")
        return False
    else:
        try:
            osdisk_tar = osdisk_raw.replace(".raw", ".tar.gz")
            cur_path = os.getcwd()
            path = f'{cur_path}/projects/{project.name}/{host.hostname}/'
            tar_path = path + osdisk_tar
            print("Starting to compress the disk image...")

            os.popen('echo "Starting to compress the disk image...">> ./logs/ansible/migration_log.txt')

            try:
                command = f'tar --format=oldgnu -Sczf {tar_path} -C {path} disk.raw'
                process2 = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
                await process2.wait()
            except Exception as e:
                print(str(e))
                return False
            else:
                raw_disk = f'{path}/disk.raw'
                if os.path.exists(raw_disk):
                    os.remove(raw_disk)
                    print("Raw disk removed after tarball creation.")

            uploaded = await upload_worker(osdisk_raw, project, disk_mountpoint, host, db)
            if not uploaded: return False

            vm_data = VMUpdate(machine_id=host.id, status=35)
            update_vm(vm_data, db)

            logger("Conversion completed for "+ osdisk_raw, "info")
            return True
        except Exception as e:
            print(str(e))
            logger(str(e), "warning")
            
            vm_data = VMUpdate(machine_id=host.id, status=-35)
            update_vm(vm_data, db)
            return False


async def start_conversion(user, project, hostname, db) -> bool:
    project = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(project.id, db)
    if hostname == ["all"]:
        hosts = get_all_machines(blueprint_id, db)
    else:
        hosts = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]

    for host in hosts:
        disks = json.loads(get_discover(project.id, db)[0].disk_details)

        for disk in disks:
            disk_raw = f'{host.hostname}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                conversion_done = await conversion_worker(disk_raw, project, disk["mnt_path"], host, db)
                if not conversion_done: return False
            except Exception as e:
                print("Conversion failed for "+ disk_raw + " :" + str(e))
                logger("Conversion failed for "+ disk_raw + " :" + str(e), "warning")
                return False
    return True