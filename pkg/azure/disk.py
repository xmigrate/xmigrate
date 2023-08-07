from pkg.azure import conversion_worker as cw
from schemas.disk import DiskUpdate
from schemas.machines import VMUpdate
from services.blueprint import get_blueprintid
from services.discover import get_discover
from services.disk import get_all_disks, update_disk
from services.machines import get_all_machines, get_machineid, get_machine_by_hostname, update_vm
from services.project import get_project_by_name
from services.storage import get_storage
from utils.logger import Logger
import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

async def start_downloading(user, project, hostname, db) -> bool:
    project = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(project.id, db)
    if isinstance(hostname, str):
        hostname = [hostname]
    for host in hostname:
        machine_id = get_machineid(host, blueprint_id, db)
        disks = json.loads(get_discover(project.id, db)[0].disk_details)
        for disk in disks:
            disk_raw = f'{host}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                downloaded = await cw.download_worker(disk_raw, project, host, machine_id, db)
                if not downloaded: return False
            except Exception as e:
                Logger.error("Download failed for %s: %s" %(disk_raw, str(e)))
                return False
        vm_data = VMUpdate(machine_id=machine_id, status=30)
        update_vm(vm_data, db)
    return True
    

async def start_conversion(user, project, hostname, db) -> bool:
    project = get_project_by_name(user, project, db)
    blueprint_id = get_blueprintid(project.id, db)
    if isinstance(hostname, str):
        hostname = [hostname]
    for host in hostname:
        machine_id = get_machineid(host, blueprint_id, db)
        disks = json.loads(get_discover(project.id, db)[0].disk_details)
        for disk in disks:
            disk_raw = f'{host}{disk["mnt_path"].replace("/", "-slash")}.raw'
            try:
                converted = await cw.conversion_worker(disk_raw, project, disk["mnt_path"], host, machine_id, db)
                if not converted: return False
            except Exception as e:
                Logger.error("Conversion failed for %s: %s" %(disk_raw, str(e)))
                return False
        vm_data = VMUpdate(machine_id=machine_id, status=35)
        update_vm(vm_data, db)
    return True


async def create_disk_worker(project, host, uri, disk_name, disk, storage_account, db) -> bool:
    creds = ServicePrincipalCredentials(client_id=project.azure_client_id, secret=project.azure_client_secret, tenant=project.azure_tenant_id)
    compute_client = ComputeManagementClient(creds, project.azure_subscription_id)
    async_creation = ''

    try:
        if disk.mnt_path in ["slash", "slashboot"]:
            async_creation = compute_client.images.create_or_update(
                project.azure_resource_group,
                disk_name,
                    {
                    'location': project.location,
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
                project.azure_resource_group,
                disk_name,
                {
                    'location': project.location,
                    'creation_data': {
                        'create_option': DiskCreateOption.import_enum,
                        'storageAccountId': f"subscriptions/{project.azure_subscription_id}/resourceGroups/{project.azure_resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account}",
                        'source_uri': uri
                    },
                }
            )
        image_resource = async_creation.result()
        
        vm_data = VMUpdate(machine_id=host.id, status=40)
        update_vm(vm_data, db)

        disk_data = DiskUpdate(disk_id=disk.id, target_disk_id=disk_name)
        update_disk(disk_data, db)

        Logger.info("Disk %s created" %(str(image_resource)))
        return True
    except Exception as e:
        Logger.error(str(e))
        
        vm_data = VMUpdate(machine_id=host.id, status=-40)
        update_vm(vm_data, db)
        return False
    

async def create_disk(user, project, hostname, db) -> bool:
    project = get_project_by_name(user, project, db)
    storage = get_storage(project.id, db)
    blueprint_id = get_blueprintid(project.id, db)

    if hostname == ["all"]:
        hosts = get_all_machines(blueprint_id, db)
    else:
        hosts = [get_machine_by_hostname(host, blueprint_id, db) for host in hostname]

    for host in hosts:
        disks = get_all_disks(host.id, db)
        for disk in disks:
            vhd = disk.vhd
            uri = f"https://{storage.bucket_name}.blob.core.windows.net/{storage.container}/{vhd}"
            disk_created = await create_disk_worker(project, host, uri, vhd.replace(".vhd",""), disk, storage.bucket_name, db)
            if not disk_created: return False
    return True