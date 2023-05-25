from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from utils.database import *
from utils.log_reader import *
from utils.logger import *
from model.project import Project
from model.disk import Disk
from model.storage import Storage
from model.blueprint import Blueprint
from model.discover import Discover
from pkg.azure import conversion_worker as cw
import os, asyncio
from azure.common.credentials import ServicePrincipalCredentials
from pkg.azure import sas
from ansible_runner import run_async

async def start_downloading(project, hostname, db):
    if isinstance(hostname, str):
        hostname = [hostname]
    for host in hostname:
        disks = (db.query(Discover).filter(Discover.project==project, Discover.host==host).first()).disk_details
        
        for disk in disks:
            disk_raw = f'{host}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                downloaded = await cw.download_worker(disk_raw, project, host, db)
                if not downloaded: return False
            except Exception as e:
                print("Download failed for "+disk_raw)
                print(str(e))
                logger("Download failed for "+disk_raw, "warning")
                logger("Here is the error: "+str(e),"warning")
                return False
    return True
    

async def start_conversion(project, hostname, db):
    if isinstance(hostname, str):
        hostname = [hostname]
    for host in hostname:
        disks = (db.query(Discover).filter(Discover.project==project, Discover.host==host).first()).disk_details
        for disk in disks:
            disk_raw = f'{host}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                converted = await cw.conversion_worker(disk_raw, project, host, db)
                if not converted: return False
            except Exception as e:
                print("Conversion failed for "+disk_raw)
                print(str(e))
                logger("Conversion failed for "+disk_raw,"warning")
                logger("Here is the error: "+str(e),"warning")
                return False
    return True

async def start_uploading(project):
    con = create_db_con()
    if Project.objects(name=project).allow_filtering()[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project).allow_filtering()
        for machine in machines:
            disks = Discover.objects(project=project, host=machine['host']).allow_filtering()[0]['disk_details']
            for disk in disks:
                disk_raw = machine['host']+disk['mnt_path'].replace('/','-slash')+".raw"
                print(disk_raw)
                try:
                    await cw.upload_worker(disk_raw,project,machine['host'])  
                except Exception as e:
                    print("Upload failed for "+disk_raw)
                    print(str(e))
                    logger("Upload failed for "+disk_raw,"warning")
                    logger("Here is the error: "+str(e),"warning")
                    return False
        con.shutdown()
        return True


async def start_cloning(project, hostname, db):
    strg = db.query(Storage).filter(Storage.project==project).first()
    prjct = db.query(Project).filter(Project.name==project).first()
    public_ip = (db.query(Discover).filter(Discover.project==project, Discover.host==hostname).first()).public_ip
    sas_token = sas.generate_sas_token(strg.storage, strg.access_key)
    url = f'https://{strg.storage}.blob.core.windows.net/{strg.container}/'
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd()
    os.popen('echo null > ./logs/ansible/migration_log.txt')

    playbook = "{}/ansible/{}/start_migration.yaml".format(current_dir, prjct.provider)
    inventory = "{}/ansible/projects/{}/hosts".format(current_dir, project)
    extravars = {
        'url': url,
        'sas': sas_token,
        'mongodb': mongodb,
        'project': project,
        'hostname': hostname,
        'ansible_user': prjct.username
    }
    envvars = {
        'ANSIBLE_BECOME_USER': prjct.username,
        'ANSIBLE_LOG_PATH': '{}/logs/ansible/{}/cloning_log.txt'.format(current_dir ,project)
    }

    cloned = await run_async(playbook=playbook, inventory=inventory, extravars=extravars, envvars=envvars, limit=public_ip, quiet=True)
    
    if (not (bool(cloned[1].stats['failures']) or bool(cloned[1].stats['dark']))):
        machines = db.query(Blueprint).filter(Blueprint.project==project).all()
        machine_count = db.query(Blueprint).filter(Blueprint.project==project).count()
        flag = True
        status_count = 0
        while flag:
            for machine in machines:
                if int(machine.status)>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
        return not flag
    else:
        return False


async def create_disk_worker(project, rg_name, uri, disk_name, location, f, mnt_path, storage_account):
    con = create_db_con()
    client_id = Project.objects(name=project).allow_filtering()[0]['client_id']
    secret = Project.objects(name=project).allow_filtering()[0]['secret']
    tenant_id = Project.objects(name=project).allow_filtering()[0]['tenant_id']
    subscription_id = Project.objects(name=project).allow_filtering()[0]['subscription_id']
    creds = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant_id)
    compute_client = ComputeManagementClient(creds,subscription_id)
    async_creation = ''
    try:
        if mnt_path in ["slash","slashboot"]:
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
        else:
            async_creation = compute_client.disks.create_or_update(
                rg_name,
                disk_name,
                {
                    'location': location,
                    'creation_data': {
                        'create_option': DiskCreateOption.import_enum,
                        'storageAccountId': "subscriptions/"+subscription_id+"/resourceGroups/"+rg_name+"/providers/Microsoft.Storage/storageAccounts/"+storage_account,
                        'source_uri': uri
                    },
                }
            )
        image_resource = async_creation.result()
        print(image_resource)
        BluePrint.objects(project=project, host="-".join(disk_name.split("-")[0:-1])).update(status='40')
        Disk.objects(project=project, host="-".join(disk_name.split("-")[0:-1]), mnt_path=mnt_path).update(disk_id=disk_name)
        logger("Disk created: "+ str(image_resource),"info")
    except Exception as e:
        logger("Disk creation failed: "+repr(e),"error")
        BluePrint.objects(project=project, host=disk_name).update(status='-40')
    finally:
        con.shutdown()

async def create_disk(project, hostname):
    con = create_db_con()
    rg_name = Project.objects(name=project).allow_filtering()[0]['resource_group']
    location = Project.objects(name=project).allow_filtering()[0]['location']
    disks = Disk.objects(project=project,host=hostname).allow_filtering()
    storage_account = Storage.objects(project=project).allow_filtering()[0]['storage']
    container = Storage.objects(project=project).allow_filtering()[0]['container']
    for disk in disks:
        vhd = disk['vhd']
        uri = "https://"+storage_account+".blob.core.windows.net/"+container+"/"+vhd
        await create_disk_worker(project,rg_name,uri,vhd.replace(".vhd",""),location,disk['file_size'],disk['mnt_path'], storage_account)
    return True
        
    

async def adhoc_image_conversion(project):
    con = create_db_con()
    if Project.objects(name=project).allow_filtering()[0]['provider'] == "azure":
        machines = BluePrint.objects(project=project).allow_filtering()
        for machine in machines:
            osdisk_raw = machine['host']+".raw"
            try:
                await asyncio.create_task(cw.conversion_worker(osdisk_raw,project,machine['host']))  
            except Exception as e:
                print("Conversion failed for "+osdisk_raw)
                print(str(e))
    con.shutdown()