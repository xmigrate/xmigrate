import os
from model.blueprint import *
from model.project import *
from model.disk import *
from model.discover import *
from utils.log_reader import *
from utils.dbconn import *
from utils.logger import *
from pkg.common import nodes as n
import time

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

import asyncio

async def call_start_build(project):
    await asyncio.create_task(start_build(project))

async def start_infra_build(project):
    rg_created = resource_group.create_rg(project)
    if rg_created:
        disk_created = await disk.create_disk(project)
        if disk_created:
            network_created = network.create_nw(project)
            if network_created:
                vm_created = compute.create_vm(project)
                if vm_created:
                    print("VM created")     
                else:
                    print("VM creation failed")
            else:
                print("Network creation failed")
        else:
            print("Disk creation failed")
    else:
        print("Resource group creation failed")

async def call_start_clone(project,hostname):
    await asyncio.create_task(start_cloning(project,hostname))

async def start_cloning(project,hostname):
    con = create_db_con()
    p = Project.objects(name=project)
    if len(p) > 0:
        nodes = []
        for host in Project.objects(name=project)[0]['public_ip']:
            nodes.append(host)
        username = Project.objects(name=project)[0]['username']
        password = Project.objects(name=project)[0]['password']
        if n.add_nodes(nodes,username,password, project, False) == False:
            logger("Cloning couldn't start because inventory not created","error")
        else:
            if p[0]['provider'] == "azure":
                logger("Cloning started","info")
                print("****************Cloning awaiting*****************")
                cloning_completed = await disk.start_cloning(project,hostname)
                if cloning_completed:
                    print("****************Cloning completed*****************")
                    logger("Disk cloning completed","info")
                else:
                    print("Disk cloning failed")
                    logger("Disk cloning failed","error")
            elif p[0]['provider'] == "aws":
                logger("Cloning started","info")
                print("****************Cloning awaiting*****************")
                cloning_completed = await awsdisk.start_cloning(project,hostname)
                if cloning_completed:
                    print("****************Cloning completed*****************")
                    logger("Cloning completed","info")
                else:
                    print("Disk cloning failed")
                    logger("Disk cloning failed","error")
            elif p[0]['provider'] == "gcp":
                logger("Cloning started","info")
                print("****************Cloning awaiting*****************")
                cloning_completed = await gcpdisk.start_cloning(project,hostname)
                if cloning_completed:
                    print("****************Cloning completed*****************")
                    logger("Cloning completed","info")
                else:
                    print("Disk cloning failed")
                    logger("Disk cloning failed","error")

async def call_start_convert(project,hostname):
    await asyncio.create_task(start_convert(project,hostname))

async def start_convert(project,hostname):
    p = Project.objects(name=project)
    if len(p) > 0:
        if p[0]['provider'] == "azure":
            logger("Download started","info")
            print("****************Download started*****************")
            image_downloaded = await disk.start_downloading(project)
            print("****************Conversion awaiting*****************")
            logger("Conversion started","info")
            if image_downloaded:
                converted =  await disk.start_conversion(project,hostname)
                if converted:
                    print("****************Conversion completed*****************")
                    logger("Disk Conversion completed","info")
                else:
                    print("Disk Conversion failed")
                    logger("Disk Conversion failed","error")
        elif p[0]['provider'] == "aws":
            logger("Conversion started","info")
            print("****************Conversion awaiting*****************")
            logger("AMI creation started","info")
            ami_created = await ami.start_ami_creation(project,hostname)
            if ami_created:
                print("****************Conversion completed*****************")
                logger("Conversion completed","info")
                logger("AMI creation completed:"+str(ami_created),"info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed","error")
        elif p[0]['provider'] == "gcp":
            logger("Conversion started","info")
            print("****************Conversion awaiting*****************")
            logger("GCP Image creation started","info")
            ami_created = await ami.start_ami_creation(project,hostname)
            if ami_created:
                print("****************Conversion completed*****************")
                logger("Conversion completed","info")
                logger("AMI creation completed:"+str(ami_created),"info")
            else:
                print("Disk Conversion failed")
                logger("Disk Conversion failed","error")


async def call_build_network(project):
    await asyncio.create_task(start_network_build(project))


# why we are not return anything from here?
async def start_network_build(project):
    con = create_db_con()
    p = Project.objects(name=project)
    if len(p) > 0:
        if p[0]['provider'] == "azure":
            logger("Network build started","info")
            print("****************Network build awaiting*****************")
            rg_created = await resource_group.create_rg(project)
            if rg_created:
                logger("Resource group created","info")
                network_created = await network.create_nw(project)
                if network_created:
                    logger("Network created","info")
                else:
                    logger("Network creation failed","error")
            else:
                print("Resource group creation failed")
                logger("Resource group creation failed","error")
        elif p[0]['provider'] == "aws":
            logger("Network creation started","info")
            network_created = await awsnw.create_nw(project)
            if network_created:
                logger("Network creation completed","info")
            else:
                print("Network creation failed")
                logger("Network creation failed","error")
        elif p[0]['provider'] == "gcp":
            logger("Network creation started","info")
            network_created = await gcpnw.create_nw(project)
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
            vm_created = await gcp_compute.build_compute(project, hostname)
            if vm_created:
                logger("ec2 creation completed","info")
            else:
                print("ec2 creation failed")
                logger("ec2 creation failed","error")


async def start_build(project):
    con = create_db_con()
    p = Project.objects(name=project)
    if len(p) > 0:
        if p[0]['provider'] == "azure":
            logger("Cloning started","info")
            print("****************Cloning awaiting*****************")
            cloning_completed = await disk.start_cloning(project)
            print("****************Cloning completed*****************")
            logger("Cloning completed","info")
            if cloning_completed:
                image_downloaded = await disk.start_downloading(project)
                if image_downloaded:
                    converted =  await disk.start_conversion(project)
                    if converted:
                        image_uploaded = await disk.start_uploading(project)
                        if image_uploaded:
                            rg_created = await resource_group.create_rg(project)
                            if rg_created:
                                disk_created = await disk.create_disk(project)
                                if disk_created:
                                    network_created = await network.create_nw(project)
                                    if network_created:
                                        vm_created = await compute.create_vm(project)
                                        if vm_created:
                                            print("VM created")
                                            logger("VM created","info")     
                                        else:
                                            print("VM creation failed")
                                            logger("VM creation failed","info")
                                    else:
                                        print("Network creation failed")
                                        logger("Network creation failed","info")
                                else:
                                    print("Disk creation failed")
                                    logger("Disk creation failed","info")
                            else:
                                print("Resource group creation failed")
                                logger("Resource group creation failed","info")
                        else:
                            print("Image uploading failed")
                            logger("Image uploading failed","info")
                    else:
                        print("Disk conversion failed")
                        logger("Disk conversion failed","info")
                else:
                    print("Image downloading failed")
                    logger("Image downloading failed","info")
            else:
                print("Disk cloning failed")
                logger("Disk cloning failed","info")
        elif p[0]['provider'] == "aws":
            logger("Cloning started","info")
            print("****************Cloning awaiting*****************")
            cloning_completed = await awsdisk.start_cloning(project)
            print("****************Cloning completed*****************")
            logger("Cloning completed","info")
            if cloning_completed:
                logger("AMI creation started","info")
                ami_created = await ami.start_ami_creation(project)
                logger("AMI creation completed:"+str(ami_created),"info")
                if ami_created:
                    logger("Network creation started","info")
                    network_created = await awsnw.create_nw(project)
                    logger("Network creation completed","info")
                    if network_created:
                        logger("EC2 creation started","info")
                        ec2_created = await ec2.build_ec2(project)
                        logger("EC2 creation completed","info")
                        if ec2_created:
                            print("ec2 creation successfull")
                        else:
                            print("ec2 creation failed")
                    else:
                        print("Network creation failed")
                else:
                    print("ami creation failed")
            else:
                print("Cloning failed")
        else:
            print("No such provider")
    else:
        print("No such project")
