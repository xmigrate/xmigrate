from pkg.azure import sas
from schemas.disk import DiskUpdate
from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.disk import get_diskid, update_disk
from services.machines import get_machineid, update_vm
from services.storage import get_storage
from utils.logger import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import os
from pathlib import Path

async def download_worker(osdisk_raw, project, host, db) -> bool:
    blueprint_id = get_blueprintid(project.id, db)
    machine_id = get_machineid(host, blueprint_id, db)
    try:
        storage = get_storage(project.id, db)
        sas_token = sas.generate_sas_token(storage.bucket_name, storage.access_key)
        cur_path = os.getcwd()
        parent = f"{cur_path}/projects/{project.name}/{host}/"

        if not os.path.exists(parent):
            os.makedirs(parent)

        path = parent + osdisk_raw

        if not os.path.exists(path):
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')

            url = f"https://{storage.bucket_name}.blob.core.windows.net/{storage.container}/{osdisk_raw}?{sas_token}"
            command1 = f"azcopy copy --recursive '{url}' '{path}'"
            
            os.popen('echo '+command1+'>> ./logs/ansible/migration_log.txt')

            process1 = await asyncio.create_subprocess_shell(command1, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process1.wait()

            vm_data = VMUpdate(machine_id=machine_id, status=30)
            update_vm(vm_data, db)
            return True
        else:
            return True
    except Exception as e:
        print(str(e))
        logger(str(e), "warning")

        vm_data = VMUpdate(machine_id=machine_id, status=-30)
        update_vm(vm_data, db)
        return False


async def upload_worker(osdisk_raw, project, disk_mountpoint, machine_id, host, db) -> bool:
    storage = get_storage(project.id, db)
    sas_token = sas.generate_sas_token(storage.bucket_name, storage.access_key)
    file_size = '0'

    try:
        osdisk_vhd = osdisk_raw.replace(".raw",".vhd")
        cur_path = os.getcwd()
        vhd_path = f"{cur_path}/projects/{project.name}/{host}/{osdisk_vhd}"
        file_size = Path(vhd_path).stat().st_size

        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "VHD uploading" >> ./logs/ansible/migration_log.txt')

        url = f"https://{storage.bucket_name}.blob.core.windows.net/{storage.container}/{osdisk_vhd}?{sas_token}"

        command3 = f"azcopy copy --recursive '{vhd_path}' '{url}'"
        process3 = await asyncio.create_subprocess_shell(command3, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()

        os.popen('echo "VHD uploaded" >> ./logs/ansible/migration_log.txt')

        vm_data = VMUpdate(machine_id=machine_id, status=32)
        update_vm(vm_data, db)

        disk_id = get_diskid(host, disk_mountpoint.replace('/', 'slash'), db)
        disk_data = DiskUpdate(disk_id=disk_id, vhd=osdisk_vhd, file_size=str(file_size))
        update_disk(disk_data, db)
        return True
    except Exception as e:
        print(str(e))
        logger(str(e), "warning")

        vm_data = VMUpdate(machine_id=machine_id, status=-32)
        update_vm(vm_data, db)

        os.popen('echo "'+ str(e) + '" >> ./logs/ansible/migration_log.txt')
        return False


async def conversion_worker(osdisk_raw, project, disk_mountpoint, host, db) -> bool:
    downloaded = await download_worker(osdisk_raw, project, host, db)
    blueprint_id = get_blueprintid(project.id, db)
    machine_id = get_machineid(host, blueprint_id, db)
    if downloaded:
        try:
            osdisk_vhd = osdisk_raw.replace(".raw", ".vhd")
            cur_path = os.getcwd()
            path = f"{cur_path}/projects/{project}/{host}/{osdisk_raw}"
            vhd_path = f"{cur_path}/projects/{project}/{host}/{osdisk_vhd}"
            print("Start converting")

            os.popen('echo "start converting">> ./logs/ansible/migration_log.txt')

            command2 = f"qemu-img convert -f raw -o subformat=fixed,force_size -O vpc {path} {vhd_path}"
            process2 = await asyncio.create_subprocess_shell(command2, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process2.wait()

            uploaded = await upload_worker(osdisk_raw, project, disk_mountpoint, machine_id, host, db)
            if not uploaded: return False

            vm_data = VMUpdate(machine_id=machine_id, status=35)
            update_vm(vm_data, db)

            logger("Conversion completed "+ osdisk_raw, "info")
            return True
        except Exception as e:
            print(str(e))
            logger(str(e),"warning")

            vm_data = VMUpdate(machine_id=machine_id, status=-35)
            update_vm(vm_data, db)
            return False
    else:
        logger("Downloading image failed", "warning")
        return False


