import os
from model.blueprint import *
from model.project import *
from model.disk import *
from utils.log_reader import *
from utils.dbconn import *
import time

from pkg.azure import network
from pkg.aws import disk as awsdisk
from pkg.azure import disk
from pkg.azure import resource_group
from pkg.azure import compute

from pkg.aws import ami
from pkg.aws import network as awsnw
from pkg.aws import ec2

import asyncio

async def call_start_build(project):
    await start_build(project)

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

async def start_build(project):
    con = create_db_con()
    print(project)
    p = Project.objects(name=project)
    print(p)
    if len(p) > 0:
        if p[0]['provider'] == "azure":
            cloning_completed = await asyncio.create_task(disk.start_cloning(project))
            if cloning_completed:
                converted =  disk.start_conversion(project)
                if converted:
                    rg_created =  resource_group.create_rg(project)
                    if rg_created:
                        disk_created =  disk.create_disk(project)
                        if disk_created:
                            network_created =  network.create_nw(project)
                            if network_created:
                                vm_created =  compute.create_vm(project)
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
                else:
                    print("Disk conversion failed")
            else:
                print("Disk cloning failed")
        elif project['provider'] == "aws":
            cloning_completed = await asyncio.create_task(awsdisk.start_cloning(project))
            if cloning_completed:
                ami_created = await ami.start_ami_creation(project)
                if ami_created:
                    network_created = await awsnw.create_nw(project)
                    if network_created:
                        ec2_created = ec2.build_ec2(project)
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
