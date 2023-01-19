import os
from ansible_runner import run_async

def run_playbook(extra_vars: dict):

    playbook = 'xmigrate.yaml'
    inventory = 'hosts'

    os.environ['ANSIBLE_LOG_PATH'] = 'log.txt'

    try:
        run_async(playbook=playbook, inventory=inventory, extravars=extra_vars)
    except Exception as e:
        print(str(e))

run_playbook(extra_vars={'mongodb':'http://15.207.235.96:8000/api', 'project': 'xmtest'})