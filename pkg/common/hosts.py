from utils.dbconn import *
from model.blueprint import *
from model.network import *

def fetch_hosts(project):
    try:
        con = create_db_con()
        response = {}
        sub_hosts = {}
        hosts = BluePrint.objects(project=project)
        for host in hosts:
            sub_name = Subnet.objects(project=project,cidr=host['subnet'])
            sub_hosts[sub_name['subnet_name']].append(host)
        for subnet in sub_hosts.keys():
            nw_name = Subnet.objects(project=project,subnet_name=subnet)
            response[nw_name['nw_name']].append(sub_hosts[subnet])
            con.close()
        return response
    except Exception as e:
        print("Reading from db failed: "+str(e))
        con.close()
        return {"msg":"Failed fetching details"}


def update_hosts(project,machines):
    try:
        con = create_db_con()
        for machine in machines:
            subnet = Subnet.objects(project=project, cidr = machine['subnet'])
            network = Network.objects(project=project, nw_name = subnet[0]['nw_name'])
            BluePrint.objects(host=machine['hostname'],project=project).update(machine_type=machine['machine_type'],public_route=machine['type'],subnet=machine['subnet'],network=network[0]['cidr'])
        con.close()
        return True
    except Exception as e:
        con.close()
        return False