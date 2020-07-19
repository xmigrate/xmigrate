import os
from model.blueprint import *
from model.project import *
from model.disk import *
from utils.log_reader import *
import time
from pkg.azure import network as nw
from pkg.azure import disk
from pkg.azure import resource_group
from pkg.azure import compute
import asyncio

     
def start_build(project):
    project = Project.objects(project=project).to_json()
    if project['provider'] == "azure":
        cloning_completed = disk.start_cloning(project)
        if cloning_completed:
            converted = asyncio.run(disk.start_conversion(project))
            if converted:
                rg_created = resource_group.create_rg(project)
                if rg_created:
                    disk_created = asyncio.run(disk.create_disk(project))
                    if disk_created:
                        network_created = asyncio.run(nw.create_network(project))
                        if network_created:
                            vm_created = asyncio.run(compute.create_vm(project))
                            if vm_created:
                                return "VM created", True    
                            else:
                                return "VM creation failed", True
                        else:
                            return "Network creation failed", True
                    else:
                        return "Disk creation failed", True
                else:
                    return "Resource group creation failed", True
            else:
                return "Disk conversion failed", True
        else:
            return "Disk cloning failed", True
    elif project['provider'] == "aws":
        print("Build failed")
