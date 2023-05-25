import os
from model.blueprint import *
from model.project import *
from model.disk import *
from model.discover import *
from model.storage import GcpBucket
from utils.log_reader import *
from utils.database import *
from utils.logger import *
from utils.playbook import run_playbook
from pkg.common import nodes as n

from pkg.azure import network
from pkg.aws import disk as awsdisk
from pkg.gcp import disk as gcpdisk
from pkg.azure import disk
from pkg.azure import resource_group
from pkg.azure import compute
from pkg.gcp import compute as gcp_compute

from pkg.aws import ami
from pkg.aws import network as awsnw
from pkg.aws import ec2

from pkg.gcp import network as gcpnw
from sqlalchemy import update

import asyncio

async def call_start_vm_preparation(project, hostname, db):
    await asyncio.create_task(start_vm_preparation(project, hostname, db))

async def start_vm_preparation(project, hostname, db):
    p = db.query(Project).filter(Project.name==project).first()

    if p is not None:
        nodes = []
        
        for ip in p.public_ip:
            nodes.append(ip)
            
        if n.add_nodes(nodes, p.username, p.password, project, db, False) == False:
            logger("VM preparation couldn't start because inventory was not created","error")
        else:
            playbook = "xmigrate.yaml"
            stage = "vm_preparation"
            curr_dir = os.getcwd()

            if p.provider == "gcp":
                storage = db.query(GcpBucket).filter(GcpBucket.project==project).first()

            extra_vars = {
                'project_id': storage.project_id,
                'gs_access_key_id': storage.access_key,
                'gs_secret_access_key': storage.secret_key
            } if p.provider == "gcp" else None

            logger("VM preparation started", "info")
            print("****************VM preparation awaiting*****************")
            try:
                preparation_completed = run_playbook(provider=p.provider, username=p.username, project_name=project, curr_working_dir=curr_dir, playbook=playbook, stage=stage, extra_vars=extra_vars)
            
                if preparation_completed:                     
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==hostname[0]
                        ).values(
                        status="21"
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    print("****************VM preparation completed*****************")
                    logger("VM preparation completed", "info")
                else:
                    print("VM preparation failed")
                    logger("VM preparation failed", "error")
            except Exception as e:
                print(str(e))

async def call_start_clone(project, hostname, db):
    await asyncio.create_task(start_cloning(project,hostname, db))

async def start_cloning(project, hostname, db):
    provider = (db.query(Project).filter(Project.name==project).first()).provider

    if provider == "azure":
        logger("Cloning started","info")
        print("****************Cloning awaiting*****************")
        cloning_completed = await disk.start_cloning(project, hostname, db)
        if cloning_completed:
            print("****************Cloning completed*****************")
            logger("Disk cloning completed","info")
        else:
            print("Disk cloning failed")
            logger("Disk cloning failed","error")
    elif provider == "aws":
        logger("Cloning started","info")
        print("****************Cloning awaiting*****************")
        cloning_completed = await awsdisk.start_cloning(project, hostname, db)
        if cloning_completed:
            print("****************Cloning completed*****************")
            logger("Cloning completed","info")
        else:
            print("Disk cloning failed")
            logger("Disk cloning failed","error")
    elif provider == "gcp":
        logger("Cloning started","info")
        print("****************Cloning awaiting*****************")
        cloning_completed = await gcpdisk.start_cloning(project, hostname, db)
        if cloning_completed:
            print("****************Cloning completed*****************")
            logger("Cloning completed","info")
        else:
            print("Disk cloning failed")
            logger("Disk cloning failed","error")

async def call_start_convert(project, hostname, db):
    await asyncio.create_task(start_convert(project, hostname, db))

async def start_convert(project, hostname, db):
    provider = (db.query(Project).filter(Project.name==project).first()).provider

    if provider == "azure":
        logger("Download started","info")
        print("****************Download started*****************")
        image_downloaded = await disk.start_downloading(project, hostname, db)
        if image_downloaded:
            print("****************Download completed*****************")
            logger("Image Download completed","info")
            print("****************Conversion awaiting*****************")
            logger("Conversion started","info")
            converted =  await disk.start_conversion(project, hostname, db)
            if converted:
                print("****************Conversion completed*****************")
                logger("Disk Conversion completed","info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed","error")
        else:
            print("Image Download failed\nDisk Conversion failed")
            logger("Image Download faied", "error")
            logger("Disk Conversion failed", "error")
    elif provider == "aws":
        logger("Conversion started","info")
        print("****************Conversion awaiting*****************")
        logger("AMI creation started","info")
        ami_created = await ami.start_ami_creation(project, hostname, db)
        if ami_created:
            print("****************Conversion completed*****************")
            logger("Conversion completed","info")
            logger("AMI creation completed:"+str(ami_created),"info")
        else:
            print("Disk Conversion failed")
            logger("Disk Conversion failed","error")
    elif provider == "gcp":
        logger("Download started","info")
        print("****************Download started*****************")
        image_downloaded = await gcpdisk.start_downloading(project, hostname, db)
        print("****************Conversion awaiting*****************")
        logger("Conversion started","info")
        if image_downloaded:
            converted =  await gcpdisk.start_conversion(project,hostname, db)
            if converted:
                print("****************Conversion completed*****************")
                logger("Disk Conversion completed","info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed","error")


async def call_build_network(project, db):
    await asyncio.create_task(start_network_build(project, db))

async def start_network_build(project, db):
    provider = (db.query(Project).filter(Project.name==project).first()).provider

    if provider == "azure":
        logger("Network build started","info")
        print("****************Network build awaiting*****************")
        rg_created = await resource_group.create_rg(project, db)
        if rg_created:
            logger("Resource group created","info")
            network_created = await network.create_nw(project, db)
            if network_created:
                logger("Network created","info")
            else:
                logger("Network creation failed","error")
        else:
            print("Resource group creation failed")
            logger("Resource group creation failed","error")
    elif provider == "aws":
        logger("Network creation started","info")
        network_created = await awsnw.create_nw(project, db)
        if network_created:
            logger("Network creation completed","info")
        else:
            print("Network creation failed")
            logger("Network creation failed","error")
    elif provider == "gcp":
        logger("Network creation started","info")
        network_created = await gcpnw.create_nw(project, db)
        if network_created:
            logger("Network creation completed","info")
        else:
            print("Network creation failed")
            logger("Network creation failed","error")

async def call_build_host(project,hostname):
    await asyncio.create_task(start_host_build(project,hostname))


async def start_host_build(project,hostname):
    con = create_db_con()
    p = Project.objects(name=project)
    if len(p) > 0:
        if p[0]['provider'] == "azure":
            logger("Host build started","info")
            print("****************Host build awaiting*****************")
            disk_created = await disk.create_disk(project,hostname)
            if disk_created:
                vm_created = await compute.create_vm(project, hostname)
            else:
                logger("Disk creation failed","error")
        elif p[0]['provider'] == "aws":
            logger("ec2 creation started","info")
            ec2_created = await ec2.build_ec2(project, hostname)
            if ec2_created:
                logger("ec2 creation completed","info")
            else:
                print("ec2 creation failed")
                logger("ec2 creation failed","error")
        elif p[0]['provider'] == "gcp":
            logger("gcp vm creation started","info")
            disk_created = await gcpdisk.start_image_creation(project, hostname)
            if disk_created:
                vm_created = await gcp_compute.build_compute(project, hostname)
                if vm_created:
                    logger("gcp vm creation completed","info")
                else:
                    print("gcp vm creation failed")
                    logger("gcp vm creation failed","error")
            else:
                print("gcp disk creation failed")
                logger("gcp disk creation failed","error")
