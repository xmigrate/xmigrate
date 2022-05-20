from utils.dbconn import *
import os
from model.blueprint import *
from model.storage import *
from model.discover import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT 
from model.discover import *
from model.project import *

async def start_cloning(project, hostname):
    con = create_db_con()
    try:
        print("bucket")
        bucket = Bucket.objects(project=project).allow_filtering()[0]['bucket']
        accesskey = Bucket.objects(project=project).allow_filtering()[0]['access_key']
        secret_key = Bucket.objects(project=project).allow_filtering()[0]['secret_key']
        print("disc")
        public_ip = Discover.objects(project=project,host=hostname).allow_filtering()[0]['public_ip']
        print("pro")
        user = Project.objects(name=project).allow_filtering()[0]['username']
        print("compl")
    except Exception as e:
        print("Error occurred: "+str(e))
    load_dotenv()
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd()
    print("/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/aws/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\"")
    if hostname == "all":
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/aws/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\""
    else:
        command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/"+project+"/hosts "+current_dir+"/ansible/aws/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\" --limit "+public_ip+" --user "+user+" --become-user "+user+" --become-method sudo"
    process = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
    await process.wait()
    machines = BluePrint.objects(project=project).allow_filtering()
    machine_count = len(machines)
    flag = True
    status_count = 0
    while flag:
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
    con.shutdown()
    return not flag