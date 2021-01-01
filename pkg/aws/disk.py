from utils.dbconn import *
import os
from model.blueprint import *
from model.storage import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT 

async def start_cloning(project):
    con = create_db_con()
    bucket = Bucket.objects(project=project)[0]['bucket']
    accesskey = Bucket.objects(project=project)[0]['access_key']
    secret_key = Bucket.objects(project=project)[0]['secret_key']
    load_dotenv()
    mongodb = os.getenv('MONGO_DB')
    current_dir = os.getcwd()
    print("/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/hosts "+current_dir+"/ansible/aws/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\"")
    command = "/usr/local/bin/ansible-playbook -i "+current_dir+"/ansible/hosts "+current_dir+"/ansible/aws/start_migration.yaml -e \"bucket="+bucket+" access_key="+accesskey+" secret_key="+secret_key+" mongodb="+mongodb+ " project="+project+"\""
    process = await asyncio.create_subprocess_shell(command, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
    await process.wait()
    machines = BluePrint.objects(project=project)
    machine_count = len(machines)
    flag = True
    status_count = 0
    while flag:
            for machine in machines:
                if int(machine['status'])>=25:
                    status_count = status_count + 1
            if status_count == machine_count:
                flag = False
    con.close()
    return not flag