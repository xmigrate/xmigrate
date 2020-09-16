from utils.dbconn import *
import os
from model.blueprint import *

async def start_cloning(project):
    con = create_db_con()
    if Project.objects(name=project)[0]['provider'] == "azure":
        storage = Storage.objects(project=project)[0]['storage']
        accesskey = Storage.objects(project=project)[0]['access_key']
        container = Storage.objects(project=project)[0]['container']
        os.popen('echo null > ./logs/ansible/migration_log.txt')
        print('ansible-playbook ./ansible/aws/start_migration.yaml > ./logs/ansible/migration_log.txt')
        os.popen('ansible-playbook ./ansible/aws/start_migration.yaml > ./logs/ansible/migration_log.txt')
        while True:
            machines = BluePrint.objects(project=project)
            machine_count = len(machines)
            print("machine count: "+str(machine_count))
            status_count = 0
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            print("status count: "+str(status_count))
            if status_count == machine_count:
                return True
            elif "PLAY RECAP" in read_migration_logs():
                if "unreachable=0" in read_migration_logs():
                    if "failed=0" in read_migration_logs():    
                        return True
                    else:
                        break
            await asyncio.sleep(60)        
    con.close()
    return False