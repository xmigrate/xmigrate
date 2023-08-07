from utils.logger import Logger
import os

def add_nodes(nodes, user, password, project) -> bool:
    ansible_host_parent = f"./ansible/projects/{project}"
    ansible_hosts = f"./ansible/projects/{project}/hosts"

    if not os.path.exists(ansible_host_parent):
       os.makedirs(ansible_host_parent)
    
    nodes = '\n'.join(nodes)
    
    try:
        with open(ansible_hosts, 'w') as hosts, open('./ansible.cfg','w') as config:
            hosts.write(f"[nodes]\n{nodes}\n[all:vars]\nansible_ssh_pass = {password}\nansible_sudo_pass = {password}")
            config.write(f"[defaults]\nremote_user = {user}\ninventory = {ansible_hosts}\nsudo_user = {user}\nhost_key_checking = false\ncommand_warnings=False\ndeprecation_warnings=False\n\n[privilege_escalation]\nbecome=True\nbecome_method=sudo\nbecome_user={user}")
        return True
    except Exception as e:
        Logger.error("Error while creating ansible configs: %s" %(str(e)))
        return False