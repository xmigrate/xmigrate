import os
from model.blueprint import *
from model.project import *



def start_cloning(project):
    if Project.objects(project=project).to_json['provider'] == "azure":
        storage = Storage.objects(project=project).to_json()['storage']
        accesskey = Storage.objects(project=project).to_json()['accesskey']
        os.popen('ansible-playbook ./ansible/azure/start_migration.yaml -e "storage="'+storage+'" accesskey='+accesskey+'"> ./logs/ansible/migration_log.txt')
     



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
