from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
from utils import dbconn
from models.project import *
from models.disk import *
from models.storage import *
from models.blueprint import *
import asyncio

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
        BluePrint.objects(project=project, host=disk_name).update(status=40)
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
        
    