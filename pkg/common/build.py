import os
from model.blueprint import *
from model.project import *
from model.disk import *
from utils.log_reader import *
import time
from pkg.azure import network as nw
from pkg.azure import disk
from pkg.azure import resource_group
import asyncio

def start_conversion(project):
    con = create_db_con()
    if Project.objects(project=project).to_json['provider'] == "azure":
        machines = BluePrint.object(project=project).to_json()
        for machine in machines:
            osdisk_raw = machine['host']+".raw"+".000"
            try:
                res,file_size = conversion_worker(osdisk_raw,project,machine['host'])
                if res:
                    BluePrint.objects(project=project,host=machine['host']).update(status='35')
                    post = Disk.objects(host=machine['host'],vhd=osdisk_raw.replace('.raw.000','.vhd'),file_size=file_size,project=project)
                    post.save()
            except:
                print("Conversion failed for "+osdisk_raw)
        return True
    con.close()



def start_cloning(project):
    con = create_db_con()
    if Project.objects(project=project).to_json['provider'] == "azure":
        storage = Storage.objects(project=project).to_json()['storage']
        accesskey = Storage.objects(project=project).to_json()['accesskey']
        os.popen('ansible-playbook ./ansible/azure/start_migration.yaml -e "storage="'+storage+'" accesskey='+accesskey+'"> ./logs/ansible/migration_log.txt')
        while "PLAY RECAP" not in read_migration_logs():
            st = 0
            BluePrint.objects(project=project).update(status=str(st))
            st = st+3
            time.sleep(60)
        if "unreachable=0" in read_migration_logs():
            if "failed=0" in read_migration_logs():    
                BluePrint.objects(project=project).update(status='30')
                return True
    return False
     

def start_build(project):
    project = Project.objects(project=project).to_json()
    if project['provider'] == "azure":
        cloning_completed = start_cloning(project)
        if cloning_completed:
            converted = start_conversion(project)
            if converted:
                rg_created = create_rg(project)
                if rg_created:
                    disk_created = asyncio.run(disk.create_disk(project))
                    if disk_created:
                        network_created = asyncio.run(nw.create_network(project))
                        if network_created:
                            vm_created = create_vm(project)
                            if vm_created:
                                return "VM created", True    
                            else:
                                return "VM creation failed", True
                        else:
                            return "Network creation failed", True
                    else:
                        return "Disk creation failed", True
                else:
                    return "Disk cloning failed", True
            elif project['provider'] == "aws":
                print("Build failed")
