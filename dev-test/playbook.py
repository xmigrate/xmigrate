import os
from ansible_runner import run_async
import asyncio

async def run_playbook(extra_vars: dict):
    playbook = os.getcwd()+'/xmigrate.yaml'
    inventory = os.getcwd()+'/hosts'
    log_path = os.getcwd()+'/log.txt'
    cmdline_args = ['-l ' + log_path]
    envvars = {
        'ANSIBLE_LOG_PATH': os.getcwd()+'/log.txt'
    }
    _, r = run_async(playbook=playbook, inventory=inventory, extravars=extra_vars, envvars=envvars)

asyncio.run(run_playbook(extra_vars={'mongodb':'http://15.207.235.96:8000/api', 'project': 'xmtest', "ANSIBLE_LOG_PATH": os.getcwd()+'/log.txt'}))