from pkg.aws import ami as awsdisk
from pkg.aws import ec2 as aws_compute
from pkg.aws.network import create_nw as aws_create_nw
from pkg.azure import compute as azure_compute
from pkg.azure import disk as azuredisk
from pkg.azure.network import create_nw as azure_create_nw
from pkg.common.cloning import clone
from pkg.common.vm_preparation import prepare
from pkg.gcp import compute as gcp_compute
from pkg.gcp import disk as gcpdisk
from pkg.gcp.network import create_nw as gcp_create_nw
from services.project import get_project_by_name
from pkg.test_header_files.test_data import migration_test_data
from utils.constants import Provider
from utils.logger import Logger


async def start_network_build(user, project, db, test_header=False):
    provider = get_project_by_name(user, project, db).provider
    network_created = False
    Logger.info("Network build started")

    if test_header:
        await migration_test_data(user, project, 20, db, None)
        network_created = True
    else:
        if provider == Provider.AZURE.value:
            network_created = await azure_create_nw(user, project, db)
        elif provider == Provider.AWS.value:
            network_created = await aws_create_nw(user, project, db)
        elif provider == Provider.GCP.value:
            network_created = await gcp_create_nw(user, project, db)

    if network_created:
        Logger.info("Network creation completed")
    else:
        Logger.critical("Network creation failed")


async def start_vm_preparation(user, project, hostname, db, test_header=False) -> None:
    Logger.info("VM preparation started")

    preparation_completed = False
    if test_header:
        await migration_test_data(user, project, 21, db, hostname)
        preparation_completed = True
    else:
        preparation_completed = await prepare(user, project, hostname, db)
        
    if preparation_completed:
        Logger.info("VM preparation completed")
    else:
        Logger.critical("VM preparation failed")


async def start_cloning(user, project, hostname, db, test_header=False) -> None:
    Logger.info("Cloning started")

    cloning_completed = False
    if test_header:
        await migration_test_data(user, project, 25, db, hostname)
        cloning_completed = True
    else:
        cloning_completed = await clone(user, project, hostname, db)

    if cloning_completed:
        Logger.info("Cloning completed")
    else:
        Logger.critical("Disk cloning failed")


async def start_conversion(user, project, hostname, db, test_header=False):
    Logger.info("Conversion started")

    provider = get_project_by_name(user, project, db).provider
    converted = False

    if test_header:
        await migration_test_data(user, project, 35, db, hostname)
        Logger.info("Disk Conversion completed")
    else:
        if provider == Provider.AWS.value:
            Logger.info("AMI creation started")
            ami_created = await awsdisk.start_ami_creation(user, project, hostname, db)
            if ami_created:
                converted = True
                Logger.info("AMI creation completed")
        if provider == Provider.AZURE.value:
            Logger.info("Download started")
            image_downloaded = await azuredisk.start_downloading(user, project, hostname, db)
            if image_downloaded:
                Logger.info("Image download completed")
                converted =  await azuredisk.start_conversion(user, project, hostname, db)
            else:
                Logger.error("Image download failed")
        if provider == Provider.GCP.value:
            converted =  await gcpdisk.start_conversion(user, project, hostname, db)

        if converted:
            Logger.info("Disk conversion completed")
        else:
            Logger.critical("Disk Conversion failed")


async def start_host_build(user, project, hostname, db, test_header=False):
    Logger.info("VM build started")

    provider = get_project_by_name(user, project, db).provider

    if test_header:
        await migration_test_data(user, project, 100, db, hostname)
        Logger.info("VM creation completed!")
    else:
        disk_created = True if provider == Provider.AWS.value else False

        if provider in (Provider.AZURE.value, Provider.GCP.value):
            if provider == 'azure':
                disk_created = await azuredisk.create_disk(user, project, hostname, db)
            elif provider == 'gcp':
                disk_created = await gcpdisk.start_image_creation(user, project, hostname, db)

            if not disk_created:
                Logger.error("Disk creation failed!")
        
        if disk_created:
            if provider == Provider.AWS.value:
                vm_created = await aws_compute.build_ec2(user, project, hostname, db)
            elif provider == Provider.AZURE.value:
                vm_created = await azure_compute.create_vm(user, project, hostname, db)
            elif provider == Provider.GCP.value:
                vm_created = await gcp_compute.build_compute(user, project, hostname, db)

            if vm_created:
                Logger.info("VM creation completed!")
            else:
                Logger.critical("VM creation failed!")