import os
from ansible_runner import run_async

def run_playbook(provider: str, username: str, project_name: str, curr_working_dir: str, playbook: str, stage: str, extra_vars: dict = None, limit: str = None):

    playbook_path = f'{curr_working_dir}/ansible/{provider}/{playbook}'
    inventory = f'{curr_working_dir}/ansible/projects/{project_name}/hosts'
    log_folder = f'{curr_working_dir}/logs/ansible/{project_name}'
    log_file = f'{log_folder}/{stage}_log.txt'
    env_vars = {
            'ANSIBLE_REMOTE_USER': username,
            'ANSIBLE_BECOME_USER': username,
            'ANSIBLE_LOG_PATH': log_file
        }
        
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    with open(log_file, 'w+'):
        try:
            runner = run_async(playbook=playbook_path, inventory=inventory, envvars=env_vars, extravars=extra_vars, limit=limit, quiet=True)
            if stage == "gather_facts":
                return(not (bool(runner[1].stats['failures']) or bool(runner[1].stats['dark'])), runner[1])
            else:
                return(not (bool(runner[1].stats['failures']) or bool(runner[1].stats['dark'])))
        except Exception as e:
            print(str(e))
