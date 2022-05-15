from model.project import *
from utils.dbconn import *
from utils.logger import *
import os


def add_nodes(nodes,user,password,p, update_db=True):
    ansible_hosts = "./ansible/"+p+"/hosts"
    if not os.path.exists("./ansible/"+p):
      os.makedirs("./ansible/"+p)
    host_file = open(ansible_hosts,'w')
    if update_db:
      try:
        Project.objects(name=p).update(public_ip=nodes, username=user, password=password)
      except Exception as e:
        print("Error while inserting to Project: "+str(e))
        logger("Error while inserting to Project: "+str(e),"error")
    nodes = '\n'.join(nodes)
    try:
      s='[nodes]'+'\n'+nodes+'\n'+'[all:vars]'+'\n'+'ansible_ssh_pass = '+password
      host_file.write(s)
      host_file.close()
      cfg_file = open('./ansible.cfg','w')
      s='[defaults]\nremote_user ='+user+'\n'+'inventory      = '+ansible_hosts+'\n'+'sudo_user      = '+user+'\n'+'host_key_checking = false\n\n'+'[privilege_escalation]\nbecome=True\nbecome_method=sudo\nbecome_user='+user
      cfg_file.write(s)
      cfg_file.close()
      return True
    except Exception as e:
      logger("Error while creating ansible cfg: "+str(e),"error")
      return False