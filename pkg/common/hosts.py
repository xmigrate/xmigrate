from model.blueprint import Blueprint
from model.network import Network, Subnet
from model.project import Project
from sqlalchemy import update

def fetch_hosts(project, db):
    try:
        response = {}
        sub_hosts = {}
        hosts = db.query(Blueprint).filter(Blueprint.project==project).all()

        for host in hosts:
            subnet_name = (db.query(Subnet).filter(Subnet.project==project, Subnet.cidr==host.subnet).first()).subnet_name
            if subnet_name not in sub_hosts.keys():
                sub_hosts[subnet_name] = []

            machine = dict(host)
            del(machine['_id'])
            sub_hosts[subnet_name].append(machine)

        for subnet in sub_hosts.keys():
            nw_name = (db.query(Subnet).filter(Subnet.project==project, Subnet.subnet_name==subnet).first()).nw_name
            if nw_name not in response.keys():
                response[nw_name] = []
            response[nw_name].append(sub_hosts[subnet])
        return response
    except Exception as e:
        print("Reading from db failed: "+repr(e))
        return {"msg":"Failed fetching details"}


def update_hosts(project, machines, db):
    try:
        for machine in machines:
            subnet = db.query(Subnet).filter(Subnet.project==project, Subnet.cidr==machine["subnet"]).first()
            network = db.query(Network).filter(Network.project==project, Network.nw_name==subnet.nw_name).first()
            provider = (db.query(Project).filter(Project.name==project).first()).provider
            if machine['public_route'] == 'Public':
                machine['public_route'] = True
            elif machine['public_route'] == 'Private':
                machine['public_route'] = False
            if provider == 'gcp':
                db.execute(update(Blueprint).where(
                    Blueprint.project==project and Blueprint.host==machine['host']
                    ).values(
                    machine_type=machine['machine_type'], public_route=machine['public_route'], subnet=machine['subnet'], network=network.nw_name
                    ).execution_options(synchronize_session="fetch"))
                db.commit()
            else:
                db.execute(update(Blueprint).where(
                    Blueprint.project==project and Blueprint.host==machine['host']
                    ).values(
                    machine_type=machine['machine_type'], public_route=machine['public_route'], subnet=machine['subnet'], network=network.cidr
                    ).execution_options(synchronize_session="fetch"))
                db.commit()
        return True
    except Exception as e:
        print(repr(e))
        return False


def fetch_all_hosts(project, db):
    try:
        subnets = db.query(Subnet).filter(Subnet.project==project).all()
        networks = db.query(Network).filter(Network.project==project).all()
        subnet_object = []
        network_objects = []
        for subnet in subnets:
            host_objects = [] 
            hosts = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.subnet==subnet.cidr).all()
            for host in hosts:
                host_objects.append(host)
            subnet_object.append({"name": subnet.subnet_name, "cidr": subnet.cidr, "subnet_type": subnet.subnet_type, "nw_name": subnet.nw_name, "hosts": host_objects})
        for network in networks:
            subs = []
            for subnet in subnet_object:
                if subnet["nw_name"] == network.nw_name:
                    subs.append(subnet)
            network_objects.append({"nw_name": network.nw_name, "cidr": network.cidr, 'subnets': subs})
        return {'networks': network_objects}
    except Exception as e:
        print(e)

