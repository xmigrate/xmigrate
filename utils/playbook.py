import os
from ansible_runner import run_async

def run_playbook(provider: str, username: str, project_name: str, curr_working_dir: str, playbook: str, stage: str, extra_vars: dict = None, limit: str = None):

    playbook_path = '{}/ansible/{}/{}'.format(curr_working_dir, provider, playbook)
    inventory = '{}/ansible/projects/{}/hosts'.format(curr_working_dir, project_name)
    log_folder = '{}/logs/ansible/{}'.format(curr_working_dir, project_name)
    log_file = '{}/{}_log.txt'.format(log_folder, stage)
    env_vars = {
            'ANSIBLE_REMOTE_USER': username,
            'ANSIBLE_BECOME_USER': username,
            'ANSIBLE_LOG_PATH': log_file
        }
        
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    with open(log_file, 'a+'):
        try:
            runner = run_async(playbook=playbook_path, inventory=inventory, envvars=env_vars, extravars=extra_vars, quiet=True, limit=limit)
            if stage != "payload_execution":
                return(not (bool(runner[1].stats['failures']) or bool(runner[1].stats['dark'])))
        except Exception as e:
            print(str(e))
    
