import os
from ansible_runner import run_async

def execute_payload(provider: str, username: str, project_name: str, curr_working_dir: str, extra_vars: dict):

    playbook = '{}/ansible/{}/payload_execution.yaml'.format(curr_working_dir, provider)
    inventory = '{}/ansible/{}/hosts'.format(curr_working_dir, project_name)
    log_folder = '{}/logs/ansible/{}'.format(curr_working_dir, project_name)
    log_file = '{}/logs/ansible/{}/log.txt'.format(curr_working_dir, project_name)
    env_vars = {
            'ANSIBLE_REMOTE_USER': username,
            'ANSIBLE_LOG_PATH': log_file
        }
        
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    with open(log_file, 'a+'):
        try:
            run_async(playbook=playbook, inventory=inventory, extravars=extra_vars, envvars=env_vars)
        except Exception as e:
            print(str(e))