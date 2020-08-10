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
            subnet_name = sub_name[0]['subnet_name']
            if subnet_name not in sub_hosts.keys():
                sub_hosts[subnet_name] = []
            machine = host.to_mongo().to_dict()
            del(machine['_id'])
            sub_hosts[subnet_name].append(machine)
        print(sub_hosts)
        for subnet in sub_hosts.keys():
            nw_name = Subnet.objects(project=project,subnet_name=subnet)
            nw_name = nw_name[0]['nw_name']
            if nw_name not in response.keys():
                response[nw_name] = []
            response[nw_name].append(sub_hosts[subnet])
            con.close()
        return response
    except Exception as e:
        print("Reading from db failed: "+repr(e))
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
        print(repr(e))
        con.close()
        return False