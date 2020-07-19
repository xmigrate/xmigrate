from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
from utils import dbconn
from models.project import *
from models.disk import *
from models.storage import *
from models.blueprint import *
from pkg.azure import conversion_worker as cw
import asyncio


async def start_conversion(project):
    con = create_db_con()
    if Project.objects(project=project).to_json['provider'] == "azure":
        machines = BluePrint.object(project=project).to_json()
        for machine in machines:
            osdisk_raw = machine['host']+".raw"+".000"
            try:
                await(asyncio.create_task(cw.conversion_worker(osdisk_raw,project,machine['host'])))       
            except:
                print("Conversion failed for "+osdisk_raw)
        return True
    con.close()



def start_cloning(project):
    con = create_db_con()
    if Project.objects(project=project).to_json['provider'] == "azure":
        storage = Storage.objects(project=project).to_json()['storage']
        accesskey = Storage.objects(project=project).to_json()['accesskey']
        os.popen('ansible-playbook ./ansible/azure/start_migration.yaml -e "storage="'+storage+'" accesskey='+accesskey+'"> ./logs/ansible/migration_log.txt')
        while "PLAY RECAP" not in read_migration_logs():
            st = 0
            BluePrint.objects(project=project).update(status=str(st))
            st = st+3
            time.sleep(60)
        if "unreachable=0" in read_migration_logs():
            if "failed=0" in read_migration_logs():    
                BluePrint.objects(project=project).update(status='30')
                return True
    return False

async def create_disk_worker(rg_name,uri,disk_name):
    con = dbconn()
    compute_client = get_client_from_cli_profile(ComputeManagementClient)
    async_creation = compute_client.images.create_or_update(
        rg_name,
        disk_name,
        {
            'location': location,
            'storage_profile': {
            'os_disk': {
                'os_type': 'Linux',
                'os_state': "Generalized",
                'blob_uri': uri,
                'caching': "ReadWrite",
            }
            }
        }
    )
    image_resource = async_creation.result()
    try:
        BluePrint.objects(project=project, host=disk_name).update(image_id=disk_name,status=40)
    except:
        print("disk creation updation failed")
    finally:
        con.close()

async def create_disk(project):
    con = dbconn()
    rg_name = Project.objects(project=project).to_json()['resource_group']
    location = Project.objects(project=project).to_json()['location']
    disks = Disk.objects(project=project).to_json()
    storage_account = Storage.objects(project=project).to_json()['storage']
    container = Storage.objects(project=project).to_json()['container']
    for disk in disks:
        vhd = Disks.objects(project=project).to_json()['vhd']
        uri = "https://"+storage_account+".blob.core.windows.net/"+container+"/"+vhd
        await(asyncio.create_task(create_disk_worker(rg_name,uri,vhd.replace(".vhd",""))))
    return True
        
    