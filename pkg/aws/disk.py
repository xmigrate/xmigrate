from utils.dbconn import *
import os
from model.blueprint import *
from model.storage import *
from model.discover import *
import asyncio
from asyncio.subprocess import PIPE, STDOUT 
from model.discover import *
from model.project import *
from ansible_runner import run_async

async def start_cloning(project):
    con = create_db_con()
    try:
        bucket = Bucket.objects(project=project).allow_filtering()[0]['bucket']
        accesskey = Bucket.objects(project=project).allow_filtering()[0]['access_key']
        secret_key = Bucket.objects(project=project).allow_filtering()[0]['secret_key']
        provider = Project.objects(name=project).allow_filtering()[0]['provider']
        user = Project.objects(name=project).allow_filtering()[0]['username']
    except Exception as e:
        print("Error occurred: "+str(e))
    load_dotenv()
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd()

    playbook = "{}/ansible/{}/start_migration.yaml".format(current_dir, provider)
    inventory = "{}/ansible/projects/{}/hosts".format(current_dir, project)
    extravars = {
        'bucket': bucket,
        'access_key': accesskey,
        'secret_key': secret_key,
        'mongodb': mongodb,
        'project': project
    }
    envvars = {
        'ANSIBLE_USER': user,
        'ANSIBLE_BECOME_USER': user,
        'ANSIBLE_LOG_PATH': '{}/logs/ansible/{}/cloning_log.txt'.format(current_dir ,project)
    }

    await run_async(playbook=playbook, inventory=inventory, extravars=extravars, envvars=envvars, quiet=True)
    
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