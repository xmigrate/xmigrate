
def add_nodes(nodes,user,password):
  host_file = open('../../ansible/hosts','w')
  nodes = '\n'.join(nodes)
  s='[nodes]'+'\n'+nodes+'\n'+'[all:vars]'+'\n'+'ansible_ssh_pass = '+password
  host_file.write(s)
  host_file.close()
  cfg_file = open('../../ansible/ansible.cfg','w')
  s='[defaults]\nremote_user ='+user+'\n'+'inventory      = ./hosts\n'+'sudo_user      = '+user+'\n'+'host_key_checking = false\n\n'+'[privilege_escalation]\nbecome=True\nbecome_method=sudo\nbecome_user='+user
  cfg_file.write(s)
  cfg_file.close()
