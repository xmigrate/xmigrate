from utils.dbconn import *
from model.blueprint import *
from model.network import *
from model.project import *

def fetch_hosts(project):
    try:
        con = create_db_con()
        response = {}
        sub_hosts = {}
        hosts = BluePrint.objects(project=project).allow_filtering()
        for host in hosts:
            sub_name = Subnet.objects(project=project,cidr=host['subnet']).allow_filtering()
            print(sub_name)
            subnet_name = sub_name[0]['subnet_name']
            if subnet_name not in sub_hosts.keys():
                sub_hosts[subnet_name] = []
            machine = dict(host)
            del(machine['_id'])
            sub_hosts[subnet_name].append(machine)
        print(sub_hosts)
        for subnet in sub_hosts.keys():
            nw_name = Subnet.objects(project=project,subnet_name=subnet).allow_filtering()
            nw_name = nw_name[0]['nw_name']
            if nw_name not in response.keys():
                response[nw_name] = []
            response[nw_name].append(sub_hosts[subnet])
            con.shutdown()
        return response
    except Exception as e:
        print("Reading from db failed: "+repr(e))
        con.shutdown()
        return {"msg":"Failed fetching details"}


def update_hosts(project,machines):
    try:
        con = create_db_con()
        for machine in machines:
            subnet = Subnet.objects(project=project, cidr = machine['subnet']).allow_filtering()
            network = Network.objects(project=project, nw_name = subnet[0]['nw_name']).allow_filtering()
            provider = Project.objects(name=project).allow_filtering()[0]['provider']
            if machine['public_route'] == 'Public':
                machine['public_route'] = True
            elif machine['public_route'] == 'Private':
                machine['public_route'] = False
            if provider == 'gcp':
                BluePrint.objects(host=machine['host'],project=project).update(machine_type=machine['machine_type'],public_route=machine['public_route'],subnet=machine['subnet'],network=network[0]['nw_name'])
            else:
                BluePrint.objects(host=machine['host'],project=project).update(machine_type=machine['machine_type'],public_route=machine['public_route'],subnet=machine['subnet'],network=network[0]['cidr'])
        con.shutdown()
        return True
    except Exception as e:
        print(repr(e))
        con.shutdown()
        return False


def fetch_all_hosts(project):
    try:
        con = create_db_con()
        subnets = Subnet.objects(project=project).allow_filtering()
        networks = Network.objects(project=project).allow_filtering()
        subnet_object = []
        network_objects = []
        for subnet in subnets:
            host_objects = [] 
            hosts = BluePrint.objects(project=project,subnet=subnet['cidr']).allow_filtering()
            for host in hosts:
                machine = dict(host)
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

