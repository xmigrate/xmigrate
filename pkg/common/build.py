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
from utils.logger import *


async def start_vm_preparation(user, project, hostname, db) -> None:
    logger("VM preparation started","info")
    print("****************VM preparation awaiting*****************")
    preparation_completed = await prepare(user, project, hostname, db)
    if preparation_completed:
        print("****************VM preparation completed*****************")
        logger("VM preparation completed", "info")
    else:
        print("VM preparation failed")
        logger("VM preparation failed", "error")


async def start_cloning(user, project, hostname, db) -> None:
    logger("Cloning started","info")
    print("****************Cloning awaiting*****************")
    cloning_completed = await clone(user, project, hostname, db)
    if cloning_completed:
        print("****************Cloning completed*****************")
        logger("Cloning completed","info")
    else:
        print("Disk cloning failed")
        logger("Disk cloning failed", "error")


async def start_conversion(user, project, hostname, db):
    provider = get_project_by_name(user, project, db).provider
    logger("Conversion started", "info")
    print("****************Conversion awaiting*****************")

    if provider == "aws":
        logger("AMI creation started", "info")
        ami_created = await awsdisk.start_ami_creation(user, project, hostname, db)
        if ami_created:
            print("****************Conversion completed*****************")
            logger("Conversion completed", "info")
            logger("AMI creation completed", "info")
        else:
            print("Disk Conversion failed")
            logger("Disk Conversion failed", "error")
    if provider in ('azure', 'gcp'):
        image_downloaded = False
        converted = False
        logger("Download started", "info")
        print("****************Download started*****************")
        if provider == 'azure':
            image_downloaded = await azuredisk.start_downloading(user, project, hostname, db)
        elif provider == 'gcp':
            image_downloaded = await gcpdisk.start_downloading(user, project, hostname, db)
        if image_downloaded:
            print("****************Download completed*****************")
            logger("Image Download completed","info")
            print("****************Conversion awaiting*****************")
            logger("Conversion started","info")
            if provider == 'azure':
                converted =  await azuredisk.start_conversion(user, project, hostname, db)
            elif provider == 'gcp':
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


async def start_network_build(user, project, db):
    provider = get_project_by_name(user, project, db).provider
    network_created = False
    logger("Network build started", "info")
    print("****************Network build awaiting*****************")

    if provider == "azure":
        network_created = await azure_create_nw(user, project, db)
    elif provider == "aws":
        network_created = await aws_create_nw(user, project, db)
    elif provider == "gcp":
        network_created = await gcp_create_nw(user, project, db)
    if network_created:
        logger("Network creation completed", "info")
    else:
        print("Network creation failed")
        logger("Network creation failed","error")


async def start_host_build(user, project, hostname, db):
    provider = get_project_by_name(user, project, db).provider
    disk_created = True if provider == 'aws' else False
    logger("VM build started", "info")

    if provider in ('azure', 'gcp'):
        if provider == 'azure':
            disk_created = await azuredisk.create_disk(user, project, hostname, db)
        elif provider == 'gcp':
            disk_created = await gcpdisk.start_image_creation(user, project, hostname, db)

        if not disk_created:
            print("Disk creation failed!")
            logger("Disk creation failed", "error")
    
    if disk_created:
        if provider == "aws":
            vm_created = await aws_compute.build_ec2(user, project, hostname, db)
        elif provider == 'azure':
            vm_created = await azure_compute.create_vm(user, project, hostname, db)
        elif provider == 'gcp':
            vm_created = await gcp_compute.build_compute(user, project, hostname, db)

        if vm_created:
            print("VM creation completed!")
            logger("VM creation completed", "info")
        else:
            print("VM creation failed!")
            logger("VM creation failed", "error")