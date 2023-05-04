from model.storage import *
from model.disk import *
from model.blueprint import * 
from utils.dbconn import *
import os
from pkg.azure import sas
from asyncio.subprocess import PIPE, STDOUT 
import asyncio
from pathlib import Path
from utils.logger import *

async def download_worker(osdisk_raw,project,host):
    con = create_db_con()
    account_name = Storage.objects(project=project).allow_filtering()[0]['storage']
    container_name = Storage.objects(project=project).allow_filtering()[0]['container']
    access_key = Storage.objects(project=project).allow_filtering()[0]['access_key']
    sas_token = sas.generate_sas_token(account_name,access_key)
    try:
        cur_path = os.getcwd()
        parent = "{}/projects/{}/{}/osdisks/".format(cur_path, project, host)
        if not os.path.exists(parent):
            os.makedirs(parent)
        path = parent+osdisk_raw
        if not os.path.exists(path):
            os.popen('echo "download started"> ./logs/ansible/migration_log.txt')
            url = f"https://{account_name}.blob.core.windows.net/{container_name}/{osdisk_raw}?{sas_token}"
            command1 = f"azcopy copy --recursive '{url}' '{path}'"
            os.popen('echo '+command1+'>> ./logs/ansible/migration_log.txt')
            process1 = await asyncio.create_subprocess_shell(command1, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
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
    account_name = Storage.objects(project=project).allow_filtering()[0]['storage']
    container_name = Storage.objects(project=project).allow_filtering()[0]['container']
    access_key = Storage.objects(project=project).allow_filtering()[0]['access_key']
    sas_token = sas.generate_sas_token(account_name,access_key)
    file_size = '0'
    try:
        osdisk_vhd = osdisk_raw.replace(".raw",".vhd")
        cur_path = os.getcwd()
        vhd_path = "{}/projects/{}/{}/osdisks/{}".format(cur_path, project, host, osdisk_vhd)
        file_size = Path(vhd_path).stat().st_size 
        os.popen('echo "Filesize calculated" >> ./logs/ansible/migration_log.txt')
        os.popen('echo "VHD uploading" >> ./logs/ansible/migration_log.txt')
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{osdisk_vhd}?{sas_token}"
        command3 = f"azcopy copy --recursive '{vhd_path}' '{url}'"
        process3 = await asyncio.create_subprocess_shell(command3, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process3.wait()
        os.popen('echo "VHD uploaded" >> ./logs/ansible/migration_log.txt')
        BluePrint.objects(project=project,host=host).update(status='36')
        Disk.objects(host=host,project=project,mnt_path=osdisk_raw.split('.raw')[0].split('-')[-1]).update(vhd=osdisk_vhd, file_size=str(file_size))
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
    downloaded = await download_worker(osdisk_raw,project,host)
    if downloaded:
        con = create_db_con()
        try:
            osdisk_vhd = osdisk_raw.replace(".raw",".vhd")
            cur_path = os.getcwd()
            path = "{}/projects/{}/{}/osdisks/{}".format(cur_path, project, host, osdisk_raw)
            vhd_path = "{}/projects/{}/{}/osdisks/{}".format(cur_path, project, host, osdisk_vhd)
            print("Start converting")
            os.popen('echo "start converting">> ./logs/ansible/migration_log.txt')
            command2 = f"qemu-img convert -f raw -o subformat=fixed,force_size -O vpc {path} {vhd_path}"
            process2 = await asyncio.create_subprocess_shell(command2, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
            await process2.wait()
            uploaded = await upload_worker(osdisk_raw,project,host)
            if not uploaded: return False
            BluePrint.objects(project=project,host=host).update(status='35')
            logger("Conversion completed "+osdisk_raw,"warning")
            return True
        except Exception as e:
            print(str(e))
            BluePrint.objects(project=project,host=host).update(status='-35')
            logger(str(e),"warning")
            return False
        finally:
            con.shutdown() 
    else:
        logger("Downloading image failed","warning")
        return False


