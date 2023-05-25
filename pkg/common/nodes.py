from model.project import *
from utils.database import *
from utils.logger import *
import os
from sqlalchemy import update

def add_nodes(nodes, user, password, p, db, update_db=True):
    ansible_hosts = "./ansible/projects/"+p+"/hosts"
    if not os.path.exists("./ansible/projects/"+p):
       os.makedirs("./ansible/projects/"+p)
    
    if update_db:
        try:
            db.execute(update(Project).where(
            Project.name==p
            ).values(
            public_ip=nodes, username=user, password=password
            ).execution_options(synchronize_session="fetch"))
            db.commit()
        except Exception as e:
            print("Error while inserting to Project: "+str(e))
            logger("Error while inserting to Project: "+str(e),"error")

    nodes = '\n'.join(nodes)
    try:
        with open(ansible_hosts, 'w') as hosts, open('./ansible.cfg','w') as config:
            hosts.write(f"[nodes]\n{nodes}\n[all:vars]\nansible_ssh_pass = {password}\nansible_sudo_pass = {password}")
            config.write(f"[defaults]\nremote_user = {user}\ninventory = {ansible_hosts}\nsudo_user = {user}\nhost_key_checking = false\ncommand_warnings=False\ndeprecation_warnings=False\n\n[privilege_escalation]\nbecome=True\nbecome_method=sudo\nbecome_user={user}")
        return True
    except Exception as e:
        logger("Error while creating ansible cfg: "+str(e),"error")
        return False