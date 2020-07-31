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
        path = "./osdisks/"+osdisk_raw
        if not os.path.exists(path):
            os.popen("az storage blob download --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_raw+" --name "+osdisk_raw+" --account-key "+access_key)
        file_size = os.popen("ls -la ./osdisks/"+osdisk_raw).readline().split()[4]
        BluePrint.objects(project=project,host=host).update(status='32')
        osdisk_vhd = osdisk_raw.replace(".raw.000",".vhd")
        os.popen("qemu-img convert -f raw -o subformat=fixed -O vpc ./osdisks/"+osdisk_raw+" ./osdisks/"+osdisk_vhd)
        BluePrint.objects(project=project,host=host).update(status='34')
        os.popen("az storage blob upload --account-name "+account_name+" --container-name "+container_name+" --file ./osdisks/"+osdisk_vhd+" --name "+osdisk_vhd+" --account-key "+access_key)
        BluePrint.objects(project=project,host=host).update(status='36')
        post = Disk(host=host,vhd=osdisk_vhd,file_size=file_size,project=project)
        post.save()
    except Exception as e:
        print(str(e))
        file_size = '0'
    finally:
        con.close() 