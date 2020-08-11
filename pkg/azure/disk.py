from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from utils.dbconn import *
from utils.log_reader import *
from model.project import *
from model.disk import *
from model.storage import *
from model.blueprint import *
from pkg.azure import conversion_worker as cw
import asyncio
import os
import asyncio, json

def start_conversion(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            osdisk_raw = machine['host']+".raw"+".000"
            try:
                cw.conversion_worker(osdisk_raw,project,machine['host'])  
            except Exception as e:
                print("Conversion failed for "+osdisk_raw)
                print(str(e))
                return False
        con.close()
        return True
    


async def start_cloning(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        storage = Storage.objects(project=project)[0]['storage']
        accesskey = Storage.objects(project=project)[0]['access_key']
        container = Storage.objects(project=project)[0]['container']
        os.popen('echo null > ./logs/ansible/migration_log.txt')
        print('ansible-playbook ./ansible/azure/start_migration.yaml -e "storage='+storage+' accesskey='+accesskey+' container='+container+'"> ./logs/ansible/migration_log.txt')
        os.popen('ansible-playbook ./ansible/azure/start_migration.yaml -e "storage='+storage+' accesskey='+accesskey+' container='+container+'"> ./logs/ansible/migration_log.txt')
        while True:
            machines = BluePrint.objects(project=project)
            machine_count = len(machines)
            print("machine count: "+str(machine_count))
            status_count = 0
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            print("status count: "+str(status_count))
            if status_count == machine_count:
                return True
            elif "PLAY RECAP" in read_migration_logs():
                if "unreachable=0" in read_migration_logs():
                    if "failed=0" in read_migration_logs():    
                        return True
                    else:
                        break
            await asyncio.sleep(60)        
    con.close()
    return False


async def create_disk_worker(project,rg_name,uri,disk_name,location,f):
    con = create_db_con()
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
                'caching': "ReadWrite"
            }
            },
            'hyper_vgeneration': 'V1'
        }
    )
    image_resource = async_creation.result()
    try:
        BluePrint.objects(project=project, host=disk_name).update(image_id=disk_name,status=40)
    except:
        print("disk creation updation failed")
    finally:
        con.close()

'''async def create_disk_worker(project,rg_name,uri,disk_name,location, file_size):
    con = create_db_con()
    com1 = f'az disk create -n {disk_name} -g {rg_name} -l {location} --for-upload --upload-size-bytes {file_size} --sku standardssd_lrs'
    com2 = f'az disk grant-access -n {disk_name} -g {rg_name} --access-level Write --duration-in-seconds 86400'
    print(com1)
    os.popen(com1).read()
    print(com2)
    sas_uri = os.popen(com2).read()
    sas_uri = json.loads(sas_uri)
    sas_uri = sas_uri['accessSas']
    com3 = f'azcopy copy "./osdisks/{disk_name}.vhd"  "{sas_uri}" --blob-type PageBlob --from-to LocalBlob'
    print(com3)
    os.popen(com3).read()
    try:
        BluePrint.objects(project=project, host=disk_name).update(image_id=disk_name,status='40')
    except Exception as e:
        print("disk creation updation failed "+str(e))
    finally:
        con.close()'''

async def create_disk(project):
    con = create_db_con()
    rg_name = Project.objects(name=project)[0]['resource_group']
    location = Project.objects(name=project)[0]['location']
    disks = Disk.objects(project=project)
    storage_account = Storage.objects(project=project)[0]['storage']
    container = Storage.objects(project=project)[0]['container']
    print(disks)
    for disk in disks:
        vhd = disk['vhd']
        uri = "https://"+storage_account+".blob.core.windows.net/"+container+"/"+vhd
        print(disk)
        await create_disk_worker(project,rg_name,uri,vhd.replace(".vhd",""),location,disk['file_size'])
    return True
        
    

async def adhoc_image_conversion(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            osdisk_raw = machine['host']+".raw"+".000"
            try:
                cw.conversion_worker(osdisk_raw,project,machine['host'])  
            except Exception as e:
                print("Conversion failed for "+osdisk_raw)
                print(str(e))
    con.close()