from ansible import context
from ansible.cli import CLI
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

def run_playbook(provider: str, username: str, project_name: str, curr_working_dir: str, extra_vars: set):

    loader = DataLoader()

    context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                        module_path=None, forks=100, remote_user=username, become=True,
                        become_method='sudo', become_user=username, verbosity=True, check=False, start_at_task=None, extra_vars=extra_vars)
    
    sources = "{}/ansible/{}/hosts".format(curr_working_dir, project_name)

    inventory = InventoryManager(loader=loader, sources=(sources))

    variable_manager = VariableManager(loader=loader, inventory=inventory, version_info=CLI.version_info(gitinfo=False))

    pbex = PlaybookExecutor(playbooks=['./ansible/{}/xmigrate.yaml'.format(provider)], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords={})

    return pbex.run()