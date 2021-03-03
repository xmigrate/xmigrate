from model.discover import *
from utils.dbconn import *
from utils.logger import *

def add_nodes(nodes,user,password):
    ansible_hosts = "'./ansible/"+project+"/hosts"
    host_file = open(ansible_hosts,'w')
    for node in nodes:
      try:
        Discover.objects(project=project).update(host="not discovered", ip="not discovered", subnet="not discovered", network="not discovered",
                  ports="not discovered", cores="not discovered", cpu_model="not discovered", ram="not discovered", disk="not discovered", 
                  public_ip=node, username=user, password=password, upsert=True)
      except Exception as e:
        print("Error while inserting to Discover: "+str(e))
        logger("Error while inserting to Discover: "+str(e),"error")
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