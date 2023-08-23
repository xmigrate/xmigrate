import os
from ansible_runner import run_async


def run_playbook(provider: str, username: str, project_name: str, curr_working_dir: str, playbook: str, stage: str, extra_vars: dict = None, limit: str = None):
    '''
    Function that runs ansible playbooks.
    Blocks the thread if run directly, so use asyncio event loops to run this.
    
    Example:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_playbook, *args)

    Returns an ansible runner runner object or boolean value True once playbook execution succeeds.
    '''

    playbook_path = f'{curr_working_dir}/ansible/{provider}/{playbook}'
    inventory = f'{curr_working_dir}/ansible/projects/{project_name}/hosts'
    log_folder = f'{curr_working_dir}/logs/ansible/{project_name}'
    log_file = f'{log_folder}/{stage}_log.txt'
    env_vars = {
            'ANSIBLE_REMOTE_USER': username,
            'ANSIBLE_BECOME_USER': username,
            'ANSIBLE_LOG_PATH': log_file,
            'ANSIBLE_HOST_KEY_CHECKING': False
        }
        
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    _, runner = run_async(playbook=playbook_path, inventory=inventory, envvars=env_vars, extravars=extra_vars, limit=limit, quiet=True)

    if any((runner.stats['failures'], runner.stats['dark'])): 
        raise RuntimeError("Playbook execution failed!")
    return runner if stage == "gather_facts" else True