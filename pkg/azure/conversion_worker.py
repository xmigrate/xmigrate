from model.storage import *
from utils import dbconn
import os

async def conversion_worker(osdisk_raw,project,host):
    con = dbconn()
    account_name = Storage.objects(project=project).to_json()['storage']
    container_name = Storage.objects(project=project).to_json()['container']
    access_key = Storage.objects(project=project).to_json()['access_key']
    pipe_result = ''
    file_size = '0'
    try:
        os.popen("az storage blob download --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_raw+" --name "+osdisk_raw+" --account-key "+access_key)
        file_size = os.popen("ls -la "+osdisk).readline().split()[4]
        BluePrint.objects(project=project,host=host).update(status='32')
        osdisk_vhd = osdisk_raw.replace(".raw.000",".vhd")
        os.popen("qemu-img convert -f raw -o subformat=fixed -O vpc ./osdisks/"+osdisk_raw+" ./osdisks/"+osdisk_vhd)
        BluePrint.objects(project=project,host=host).update(status='34')
        os.popen("az storage blob upload --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_vhd+" --name "+osdisk_vhd+" --account-key "+access_key")
        BluePrint.objects(project=project,host=host).update(status='36')
        post = Disk.objects(host=host],vhd=osdisk_vhd),file_size=file_size,project=project)
        post.save()
    except:
        file_size = '0'
    finally:
        con.close()