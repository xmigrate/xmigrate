from model.blueprint import Blueprint
from model.discover import Discover
from model.disk import Disk
from model.project import Project
from model.storage import Storage
from pkg.azure import conversion_worker as cw
from utils.logger import *
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