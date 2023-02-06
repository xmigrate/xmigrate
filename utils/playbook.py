import os
from ansible_runner import run_async
from utils.logger import logger

def execute_payload(provider: str, username: str, project_name: str, curr_working_dir: str, extra_vars: dict):

    playbook = '{}/ansible/{}/payload_execution.yaml'.format(curr_working_dir, provider)
    inventory = '{}/ansible/projects/{}/hosts'.format(curr_working_dir, project_name)
    log_folder = '{}/logs/ansible/{}'.format(curr_working_dir, project_name)
    log_file = '{}/logs/ansible/{}/payload_log.txt'.format(curr_working_dir, project_name)
    env_vars = {
            'ANSIBLE_REMOTE_USER': username,
            'ANSIBLE_LOG_PATH': log_file
        }
        
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    with open(log_file, 'a+'):
        try:
            logger("Payload execution started", 'info')
            run_async(playbook=playbook, inventory=inventory, extravars=extra_vars, envvars=env_vars)
            logger("Payload execution successful", 'info')
        except Exception as e:
            print(str(e))
            logger("Payload execution failed", 'info')

def prepare_vm(provider: str, username: str, project_name: str, curr_working_dir: str):

    playbook = '{}/ansible/{}/xmigrate.yaml'.format(curr_working_dir, provider)
    inventory = '{}/ansible/projects/{}/hosts'.format(curr_working_dir, project_name)
    log_file = '{}/logs/ansible/{}/prep_log.txt'.format(curr_working_dir, project_name)
    env_vars = {
            'ANSIBLE_REMOTE_USER': username,
            'ANSIBLE_BECOME_USER': username,
            'ANSIBLE_LOG_PATH': log_file
        }

    with open(log_file, 'a+'):
        try:
            logger("VM preparation started", 'info')
            run_async(playbook=playbook, inventory=inventory, envvars=env_vars)
            logger("VM preparation successful", 'info')
        except Exception as e:
            print(str(e))
            logger("VM preparation failed", 'info')