import os
from model.blueprint import *
from model.project import *
from utils.log_reader import *
import sleep

#cloning should do conversion also
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

#def create_disk(project):

     

def start_build(project):
    project = Project.objects(project=project).to_json()
    if project['provider'] == "azure":
        cloning_completed = start_cloning(project)
        if cloning_completed:
            disk_created = create_disk(project)
            if disk_created:
                network_created = create_network(project)
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
