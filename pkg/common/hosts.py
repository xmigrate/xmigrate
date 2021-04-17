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
            print(sub_name)
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
        logger(str(e),"warning")
        con.close()
        return {"msg":"Failed fetching details"}


def update_hosts(project,machines):
    try:
        con = create_db_con()
        for machine in machines:
            subnet = Subnet.objects(project=project, cidr = machine['subnet'])
            network = Network.objects(project=project, nw_name = subnet[0]['nw_name'])
            if machine['public_route'] == 'Public':
                machine['public_route'] = True
            elif machine['public_route'] == 'Private':
                machine['public_route'] = False
            BluePrint.objects(host=machine['host'],project=project).update(machine_type=machine['machine_type'],public_route=machine['public_route'],subnet=machine['subnet'],network=network[0]['cidr'])
        con.close()
        return True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")
        con.close()
        return False


def fetch_all_hosts(project):
    try:
        con = create_db_con()
        subnets = Subnet.objects(project=project)
        networks = Network.objects(project=project)
        subnet_object = []
        network_objects = []
        for subnet in subnets:
            host_objects = [] 
            hosts = BluePrint.objects(project=project,subnet=subnet['cidr'])
            for host in hosts:
                machine = host.to_mongo().to_dict()
                del(machine['_id'])
                host_objects.append(machine)
            subnet_object.append({"name":subnet['subnet_name'],"cidr":subnet['cidr'],"subnet_type":subnet['subnet_type'],"nw_name":subnet['nw_name'],"hosts":host_objects})
        for network in networks:
            subs = []
            for subnet in subnet_object:
                if subnet['nw_name'] == network['nw_name']:
                    subs.append(subnet)
            network_objects.append({"nw_name":network['nw_name'], "cidr":network['cidr'],'subnets':subs})
        return {'networks':network_objects}
    except Exception as e:
        print(e)
        logger(str(e),"warning")

