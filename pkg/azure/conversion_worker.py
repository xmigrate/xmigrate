from model.storage import *
from model.disk import *
from model.blueprint import * 
from utils.dbconn import *
import os

def conversion_worker(osdisk_raw,project,host):
    con = create_db_con()
    account_name = Storage.objects(project=project)[0]['storage']
    container_name = Storage.objects(project=project)[0]['container']
    access_key = Storage.objects(project=project)[0]['access_key']
    pipe_result = ''
    file_size = '0'
    try:
        osdisk_vhd = osdisk_raw.replace(".raw.000",".vhd")
        path = "./osdisks/"+osdisk_raw
        if not os.path.exists(path):
            os.popen("az storage blob download --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_raw+" --name "+osdisk_raw+" --account-key "+access_key).read()
        BluePrint.objects(project=project,host=host).update(status='32')
        print("Start converting")
        print(path)
        os.popen("qemu-img convert -f raw -o subformat=fixed,force_size -O vpc ./osdisks/"+osdisk_raw+" ./osdisks/"+osdisk_vhd).read()
        BluePrint.objects(project=project,host=host).update(status='34')
        file_size = os.popen("ls -la ./osdisks/"+osdisk_vhd).readline().split()[4]
        os.popen("az storage blob upload --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_vhd+" --name "+osdisk_vhd+" --account-key "+access_key).read()
        BluePrint.objects(project=project,host=host).update(status='36')
        Disk.objects(host=host,project=project).update_one(vhd=osdisk_vhd, file_size=file_size, upsert=True)
    except Exception as e:
        print(str(e))
        file_size = '0'
    finally:
        con.close() 