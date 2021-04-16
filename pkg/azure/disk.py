from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from utils.dbconn import *
from utils.log_reader import *
from utils.logger import *
from model.project import *
from model.disk import *
from model.storage import *
from model.blueprint import *
from pkg.azure import conversion_worker as cw
import os
import asyncio, json
from asyncio.subprocess import PIPE, STDOUT 
from azure.common.credentials import ServicePrincipalCredentials
from dotenv import load_dotenv
from os import getenv
import shlex, subprocess
from pkg.azure import sas

async def start_downloading(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            osdisk_raw = machine['host']+".raw"
            try:
                await cw.download_worker(osdisk_raw,project,machine['host'])  
            except Exception as e:
                print("Download failed for "+osdisk_raw)
                print(str(e))
                logger("Download failed for "+osdisk_raw,"warning")
                logger("Here is the error: "+str(e),"warning")
                return False
        con.close()
        return True
    

async def start_conversion(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            osdisk_raw = machine['host']+".raw"
            try:
                await cw.conversion_worker(osdisk_raw,project,machine['host'])  
            except Exception as e:
                print("Conversion failed for "+osdisk_raw)
                print(str(e))
                logger("Conversion failed for "+osdisk_raw,"warning")
                logger("Here is the error: "+str(e),"warning")
                return False
        con.close()
        return True

async def start_uploading(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            osdisk_raw = machine['host']+".raw"
            try:
                await cw.upload_worker(osdisk_raw,project,machine['host'])  
            except Exception as e:
                print("Upload failed for "+osdisk_raw)
                print(str(e))
                logger("Upload failed for "+osdisk_raw,"warning")
                logger("Here is the error: "+str(e),"warning")
                return False
        con.close()
        return True


async def start_cloning(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        storage = Storage.objects(project=project)[0]['storage']
        accesskey = Storage.objects(project=project)[0]['access_key']
        container = Storage.objects(project=project)[0]['container']
        sas_token = sas.generate_sas_token(storage,accesskey)
        url = "https://" + storage + ".blob.core.windows.net/" + container + "/"
        load_dotenv()
        mongodb = os.getenv('MONGO_DB')
        current_dir = os.getcwd()
        os.popen('echo null > ./logs/ansible/migration_log.txt')
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/hosts "+current_dir+"/ansible/azure/start_migration.yaml -e \"url="+url+" sas="+sas_token+" mongodb="+mongodb+ " project="+project+"\""
        process = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        await process.wait()
        machines = BluePrint.objects(project=project)
        machine_count = len(machines)
        flag = True
        status_count = 0
        while flag:
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
        con.close()
        return not flag


async def create_disk_worker(project,rg_name,uri,disk_name,location,f):
    con = create_db_con()
    client_id = Project.objects(name=project)[0]['client_id']
    secret = Project.objects(name=project)[0]['secret']
    tenant_id = Project.objects(name=project)[0]['tenant_id']
    subscription_id = Project.objects(name=project)[0]['subscription_id']
    creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
    compute_client = ComputeManagementClient(creds,subscription_id)
    con.close()
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
                'storage_account_type': 'StandardSSD_LRS'
                
            }
            },
            'hyper_vgeneration': 'V1'
        }
    )
    image_resource = async_creation.result()
    try:
        BluePrint.objects(project=project, host=disk_name).update(image_id=disk_name,status='40')
    except Exception as e:
        print("disk creation updation failed: "+repr(e))
        logger("Disk creation updation failed: "+repr(e),"warning")
    finally:
        con.close()

async def create_disk(project):
    con = create_db_con()
    rg_name = Project.objects(name=project)[0]['resource_group']
    location = Project.objects(name=project)[0]['location']
    disks = Disk.objects(project=project)
    storage_account = Storage.objects(project=project)[0]['storage']
    container = Storage.objects(project=project)[0]['container']
    for disk in disks:
        vhd = disk['vhd']
        uri = "https://"+storage_account+".blob.core.windows.net/"+container+"/"+vhd
        await create_disk_worker(project,rg_name,uri,vhd.replace(".vhd",""),location,disk['file_size'])
    return True
        
    

async def adhoc_image_conversion(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project)
        for machine in machines:
            osdisk_raw = machine['host']+".raw"
            try:
                await asyncio.create_task(cw.conversion_worker(osdisk_raw,project,machine['host']))  
            except Exception as e:
                print("Conversion failed for "+osdisk_raw)
                print(str(e))
                logger(str(e),"warning")
    con.close()