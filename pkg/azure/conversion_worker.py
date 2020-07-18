from model.storage import *
from utils import dbconn
import os

def conversion_worker(osdisk_raw,project,host):
    con = dbconn()
    account_name = Storage.objects(project=project).to_json()['storage']
    container_name = Storage.objects(project=project).to_json()['container']
    access_key = Storage.objects(project=project).to_json()['access_key']
    pipe_result = ''
    try:
        os.popen("az storage blob download --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_raw+" --name "+osdisk_raw+" --account-key "+access_key)
        file_size = os.popen("ls -la "+osdisk).readline().split()[4]
        BluePrint.objects(project=project,host=host).update(status='32')
        os.popen("qemu-img convert -f raw -o subformat=fixed -O vpc ./osdisks/"+osdisk_raw+" ./osdisks/"+osdisk_raw.replace(".raw.000",".vhd"))
        BluePrint.objects(project=project,host=host).update(status='34')
        return True, file_size
    except:
        file_size = '0'
        return False, file_size
    finally:
        con.close()