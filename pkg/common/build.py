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
from test_header_files.test_data import migration_test_data
from utils.constants import Provider
from utils.logger import *


async def start_network_build(user, project, db, test_header=False):
    provider = get_project_by_name(user, project, db).provider
    network_created = False
    logger("Network build started", "info")
    print("****************Network build awaiting*****************")

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
        logger("Network creation completed", "info")
    else:
        print("Network creation failed")
        logger("Network creation failed","error")


async def start_vm_preparation(user, project, hostname, db, test_header=False) -> None:
    logger("VM preparation started","info")
    print("****************VM preparation awaiting*****************")

    preparation_completed = False
    if test_header:
        await migration_test_data(user, project, 21, db, hostname)
        preparation_completed = True
    else:
        preparation_completed = await prepare(user, project, hostname, db)
        
    if preparation_completed:
        print("****************VM preparation completed*****************")
        logger("VM preparation completed", "info")
    else:
        print("VM preparation failed")
        logger("VM preparation failed", "error")


async def start_cloning(user, project, hostname, db, test_header=False) -> None:
    logger("Cloning started","info")
    print("****************Cloning awaiting*****************")

    cloning_completed = False
    if test_header:
        await migration_test_data(user, project, 25, db, hostname)
        cloning_completed = True
    else:
        cloning_completed = await clone(user, project, hostname, db)

    if cloning_completed:
        print("****************Cloning completed*****************")
        logger("Cloning completed","info")
    else:
        print("Disk cloning failed")
        logger("Disk cloning failed", "error")


async def start_conversion(user, project, hostname, db, test_header=False):
    logger("Conversion started", "info")
    print("****************Conversion awaiting*****************")

    provider = get_project_by_name(user, project, db).provider

    if test_header:
        await migration_test_data(user, project, 35, db, hostname)
        print("Disk Conversion completed")
        logger("Disk Conversion completed", "error")
    else:
        provider = get_project_by_name(user, project, db).provider
        logger("Conversion started", "info")
        print("****************Conversion awaiting*****************")

        if provider == Provider.AWS.value:
            logger("AMI creation started", "info")
            ami_created = await awsdisk.start_ami_creation(user, project, hostname, db)
            if ami_created:
                print("****************Conversion completed*****************")
                logger("Conversion completed", "info")
                logger("AMI creation completed", "info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed", "error")
        if provider in (Provider.AZURE.value, Provider.GCP.value):
            image_downloaded = False
            converted = False
            logger("Download started", "info")
            print("****************Download started*****************")
            if provider == Provider.AZURE.value:
                image_downloaded = await azuredisk.start_downloading(user, project, hostname, db)
            elif provider == Provider.GCP.value:
                image_downloaded = await gcpdisk.start_downloading(user, project, hostname, db)
            if image_downloaded:
                print("****************Download completed*****************")
                logger("Image Download completed","info")
                print("****************Conversion awaiting*****************")
                logger("Conversion started","info")
                if provider == Provider.AZURE.value:
                    converted =  await azuredisk.start_conversion(user, project, hostname, db)
                elif provider == Provider.GCP.value:
                    converted =  await gcpdisk.start_conversion(user, project, hostname, db)
                if converted:
                    print("****************Conversion completed*****************")
                    logger("Disk Conversion completed", "info")
                else:
                    print("Disk Conversion failed")
                    logger("Disk Conversion failed", "error")
            else:
                print("Image Download failed\nDisk Conversion failed")
                logger("Image Download faied", "error")
                logger("Disk Conversion failed", "error")


async def start_host_build(user, project, hostname, db, test_header=False):
    provider = get_project_by_name(user, project, db).provider

    if test_header:
        await migration_test_data(user, project, 100, db, hostname)
        print("VM creation completed!")
        logger("VM creation completed", "info")
    else:
        disk_created = True if provider == Provider.AWS.value else False
        logger("VM build started", "info")

        if provider in (Provider.AZURE.value, Provider.GCP.value):
            if provider == 'azure':
                disk_created = await azuredisk.create_disk(user, project, hostname, db)
            elif provider == 'gcp':
                disk_created = await gcpdisk.start_image_creation(user, project, hostname, db)

            if not disk_created:
                print("Disk creation failed!")
                logger("Disk creation failed", "error")
        
        if disk_created:
            if provider == Provider.AWS.value:
                vm_created = await aws_compute.build_ec2(user, project, hostname, db)
            elif provider == Provider.AZURE.value:
                vm_created = await azure_compute.create_vm(user, project, hostname, db)
            elif provider == Provider.GCP.value:
                vm_created = await gcp_compute.build_compute(user, project, hostname, db)

            if vm_created:
                print("VM creation completed!")
                logger("VM creation completed", "info")
            else:
                print("VM creation failed!")
                logger("VM creation failed", "error")