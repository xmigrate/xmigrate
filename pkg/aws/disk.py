from utils.dbconn import *
import os
from model.blueprint import *
from model.storage import *
from model.discover import *
from utils.playbook import run_playbook
import asyncio
from asyncio.subprocess import PIPE, STDOUT 
from model.discover import *
from model.project import *

async def start_cloning(project, hostname):
    con = create_db_con()
    try:
        bucket = Bucket.objects(project=project).allow_filtering()[0]['bucket']
        access_key = Bucket.objects(project=project).allow_filtering()[0]['access_key']
        secret_key = Bucket.objects(project=project).allow_filtering()[0]['secret_key']
        public_ip = Discover.objects(project=project,host=hostname).allow_filtering()[0]['public_ip']
        user = Project.objects(name=project).allow_filtering()[0]['username']
    except Exception as e:
        print("Error occurred: "+str(e))
    load_dotenv()
    username = Project.objects(name=project)[0]['username']
    mongodb = os.getenv('BASE_URL')
    current_dir = os.getcwd() 
    playbook = "start_migration.yaml"
    stage = "start clone"
    provider = Project.objects(name=project)[0]['provider']
    # print(provider)
    # print(project)
    extra_vars = {'bucket': bucket, 'access_key': access_key, 'secret_key': secret_key, 'mongodb': mongodb, 'project': project, 'public_ip': public_ip, 'user': user} 
    # cloning_complets = 
    # print(extra_vars)
    if hostname == "all":
        run_playbook(username=username,provider=provider,project_name=project, curr_working_dir=current_dir, playbook=playbook, stage=stage, extra_vars=extra_vars)
    else:
        run_playbook(username=username,provider=provider,project_name=project, curr_working_dir=current_dir, playbook=playbook, stage=stage, extra_vars=extra_vars)
    
    # if cloning_complets:
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