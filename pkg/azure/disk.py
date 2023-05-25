from model.blueprint import Blueprint
from model.discover import Discover
from model.disk import Disk
from model.project import Project
from model.storage import Storage
from pkg.azure import conversion_worker as cw
from pkg.azure import sas
from utils.logger import *
import os
from ansible_runner import run_async
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from sqlalchemy import update

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


async def create_disk_worker(project, rg_name, uri, disk_name, location, mnt_path, storage_account, db):
    prjct = db.query(Project).filter(Project.name==project).first()
    creds = ServicePrincipalCredentials(client_id=prjct.client_id, secret=prjct.secret, tenant=prjct.tenant_id)
    compute_client = ComputeManagementClient(creds, prjct.subscription_id)
    async_creation = ''

    try:
        if mnt_path in ["slash", "slashboot"]:
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
                        'storageAccountId': f"subscriptions/{prjct.subscription_id}/resourceGroups/{rg_name}/providers/Microsoft.Storage/storageAccounts/{storage_account}",
                        'source_uri': uri
                    },
                }
            )
        image_resource = async_creation.result()
        print(image_resource)

        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==disk_name.replace("-slash", "")
            ).values(
            status='40'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        db.execute(update(Disk).where(
            Disk.project==project and Disk.host==disk_name.replace("-slash", "") and Disk.mnt_path==mnt_path
            ).values(
            disk_id=disk_name
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        logger("Disk created: "+ str(image_resource),"info")
        return True
    except Exception as e:
        logger("Disk creation failed: "+repr(e),"error")
        
        db.execute(update(Blueprint).where(
            Blueprint.project==project and Blueprint.host==disk_name.replace("-slash", "")
            ).values(
            status='-40'
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        return False
    

async def create_disk(project, hostname, db):
    prjct = db.query(Project).filter(Project.name==project).first()
    strg = db.query(Storage).filter(Storage.project==project).first()
    disks = db.query(Disk).filter(Disk.project==project, Disk.host==hostname).all()

    for disk in disks:
        vhd = disk.vhd
        uri = f"https://{strg.storage}.blob.core.windows.net/{strg.container}/{vhd}"
        disk_created = await create_disk_worker(
            project, prjct.resource_group, uri, vhd.replace(".vhd",""), prjct.location, disk.mnt_path, strg.storage, db
            )
        if not disk_created: return False
    return True