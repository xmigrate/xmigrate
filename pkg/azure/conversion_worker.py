from model.blueprint import Blueprint
from model.disk import Disk
from model.storage import Storage
from pkg.azure import sas
from utils.logger import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import os
from pathlib import Path
from sqlalchemy import update

async def download_worker(osdisk_raw, project, host, db):
    strg = db.query(Storage).filter(Storage.project==project).first()
    sas_token = sas.generate_sas_token(strg.storage, strg.access_key)

    try:
        cur_path = os.getcwd()
        parent = f"{cur_path}/projects/{project}/{host}/"

        if not os.path.exists(parent):
            os.makedirs(parent)

        path = parent+osdisk_raw

        if not os.path.exists(path):
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')

            url = f"https://{strg.storage}.blob.core.windows.net/{strg.container}/{osdisk_raw}?{sas_token}"
            command1 = f"azcopy copy --recursive '{url}' '{path}'"
            
            os.popen('echo '+command1+'>> ./logs/ansible/migration_log.txt')

            process1 = await asyncio.create_subprocess_shell(command1, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
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
    strg = db.query(Storage).filter(Storage.project==project).first()
    sas_token = sas.generate_sas_token(strg.storage, strg.access_key)
    file_size = '0'

    try:
        osdisk_vhd = osdisk_raw.replace(".raw",".vhd")
        cur_path = os.getcwd()
        vhd_path = f"{cur_path}/projects/{project}/{host}/{osdisk_vhd}"
        file_size = Path(vhd_path).stat().st_size

        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "VHD uploading" >> ./logs/ansible/migration_log.txt')

        url = f"https://{strg.storage}.blob.core.windows.net/{strg.container}/{osdisk_vhd}?{sas_token}"

        command3 = f"azcopy copy --recursive '{vhd_path}' '{url}'"
        process3 = await asyncio.create_subprocess_shell(command3, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()

        os.popen('echo "VHD uploaded" >> ./logs/ansible/migration_log.txt')

        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==host
            ).values(
            status='36'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        db.execute(update(Disk).where(
            Disk.project==project and Disk.host==host and Disk.mnt_path==osdisk_raw.split('.raw')[0].split('-')[-1]
            ).values(
            vhd=osdisk_vhd, file_size=str(file_size)
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

            uploaded = await upload_worker(osdisk_raw, project, host, db)
            if not uploaded: return False

            db.execute(update(Blueprint).where(
                Blueprint.project==project and Blueprint.host==host
                ).values(
                status='35'
                ).execution_options(synchronize_session="fetch"))
            db.commit()

            logger("Conversion completed "+osdisk_raw ,"info")
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
        logger("Downloading image failed", "warning")
        return False


