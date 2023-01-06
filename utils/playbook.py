from ansible import context
from ansible.cli import CLI
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

def run_playbook(username, mongodb_url, project_name, provider=None, curr_working_dir=None, project_id=None, gs_access_key_id=None, gs_secret_access_key=None):

    loader = DataLoader()

    context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                        module_path=None, forks=100, remote_user=username, become=True,
                        become_method='sudo', become_user=username, verbosity=True, check=False, start_at_task=None)

    inventory = InventoryManager(loader=loader, sources=("{current_dir}+/ansible/+{project}+/hosts"))

    variable_manager = VariableManager(loader=loader, inventory=inventory, version_info=CLI.version_info(gitinfo=False))
    variable_manager.extra_vars = {"mongodb": mongodb_url, "project": project_name}

    pbex = PlaybookExecutor(playbooks=['./ansible/aws/xmigrate.yaml'], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords={})

    return pbex.run()