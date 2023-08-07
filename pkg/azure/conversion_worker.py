from pkg.azure import sas
from schemas.disk import DiskUpdate
from schemas.machines import VMUpdate
from services.disk import get_diskid, update_disk
from services.machines import update_vm
from services.storage import get_storage
from utils.logger import Logger
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import json
import os
from pathlib import Path


async def download_worker(osdisk_raw, project, host, machine_id, db) -> bool:
    try:
        storage = get_storage(project.id, db)
        sas_token = sas.generate_sas_token(storage.bucket_name, storage.access_key)
        cur_path = os.getcwd()
        parent = f"{cur_path}/projects/{project.name}/{host}/"

        if not os.path.exists(parent):
            os.makedirs(parent)

        path = parent + osdisk_raw

        if not os.path.exists(path):
            Logger.info("Downloading disk %s..." %osdisk_raw)
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')

            url = f"https://{storage.bucket_name}.blob.core.windows.net/{storage.container}/{osdisk_raw}?{sas_token}"
            command1 = f"azcopy copy --recursive '{url}' '{path}'"
            
            os.popen('echo '+command1+'>> ./logs/ansible/migration_log.txt')

            process1 = await asyncio.create_subprocess_shell(command1, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process1.wait()

            return True
        else:
            Logger.info("Raw disk already downloaded!")
            return True
    except Exception as e:
        Logger.error(str(e))

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

        disk_id = get_diskid(machine_id, disk_mountpoint.replace('/', 'slash'), db)
        disk_data = DiskUpdate(disk_id=disk_id, vhd=osdisk_vhd, file_size=str(file_size))
        update_disk(disk_data, db)
        return True
    except Exception as e:
        Logger.error(str(e))

        vm_data = VMUpdate(machine_id=machine_id, status=-32)
        update_vm(vm_data, db)

        os.popen('echo "'+ str(e) + '" >> ./logs/ansible/migration_log.txt')
        return False


async def get_size(path) -> int:
    qemu_command = ['qemu-img', 'info', '-f', 'raw', '--output', 'json', path]
    process = await asyncio.create_subprocess_exec(*qemu_command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f'Error executing command: {stderr.decode()}')
    output_json = json.loads(stdout.decode())
    size = output_json['virtual-size']
    return int(size)


async def conversion_worker(osdisk_raw, project, disk_mountpoint, host, machine_id, db) -> bool:
    try:
        osdisk_vhd = osdisk_raw.replace(".raw", ".vhd")
        cur_path = os.getcwd()
        path = f"{cur_path}/projects/{project.name}/{host}/{osdisk_raw}"
        vhd_path = f"{cur_path}/projects/{project.name}/{host}/{osdisk_vhd}"
        Logger.info("Starting conversion...")

        os.popen('echo "start converting">> ./logs/ansible/migration_log.txt')
        convert_command = f"qemu-img convert -f raw -o subformat=fixed,force_size -O vpc {path} {vhd_path}"

        MB = 1024 * 1024
        size = await get_size(path)
        rounded_size = ((size // MB) + 1) * MB
        if size % MB == 0:
            Logger.info("Size is already rounded")
            process = await asyncio.create_subprocess_shell(convert_command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process.wait()
        else:
            Logger.info("Size before conversion: %s" %(str(size)))
            resize_command = f"qemu-img resize -f raw {path} {rounded_size}"
            process = await asyncio.create_subprocess_shell(resize_command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process.wait()
            process = await asyncio.create_subprocess_shell(convert_command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process.wait()
            size = await get_size(path)
            Logger.info("Size after conversion: %s" %(str(size)))

        uploaded = await upload_worker(osdisk_raw, project, disk_mountpoint, machine_id, host, db)
        if not uploaded: return False

        Logger.info("Conversion completed %s" %osdisk_raw)
        return True
    except Exception as e:
        Logger.error(str(e))
        vm_data = VMUpdate(machine_id=machine_id, status=-35)
        update_vm(vm_data, db)
        return False