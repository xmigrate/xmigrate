from model.blueprint import Blueprint
from model.discover import Discover
from model.network import Network, Subnet
from model.project import Project
# from utils.converter import conv_KB
from collections import defaultdict
from sqlalchemy import update, delete

def update_nw_cidr(p, db):
    machines = db.query(Discover).filter(Discover.project==p).all()
    networks = []
    print("trying to update network")
    for machine in machines:
        networks.append(machine.network)
    networks = list(set(networks))
    vpc_cidr = defaultdict(list)
    for i in machines:
        vpc_cidr[i.network].append(i.subnet)
    for key in vpc_cidr.keys():
        subnet_prefixes = []
        for j in vpc_cidr[key]:
            subnet_prefixes.append(int(j.split('/')[-1]))
            if '/' not in i:
                try:
                    db.execute(update(Discover).where(
                        Discover.network==i and Discover.project==p
                        ).values(
                        Network=p
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()
                except:
                    print("Failed upating network")
    return True


def update_subnet(cidr, p, db):
    print("trying to update subnet")
    machines = db.query(Discover).filter(Discover.project==p).all()
    if cidr == '10.0.0.0':
        for machine in machines:
            if machine.network.split('.')[0] == '10':
                continue
            machine.ip = machine.ip.split('.')
            (machine.ip)[0] = '10'
            machine.ip = '.'.join(machine.ip)
            machine.network = machine.network.split('.')
            (machine.network)[0] = '10'
            machine.network = '.'.join(machine.network)
            machine.subnet = machine.subnet.split('.')
            (machine.subnet)[0] = '10'
            machine.subnet = '.'.join(machine.subnet)
           # print machine
    elif cidr == '172.16.0.0':
        for machine in machines:
            if machine.network.split('.')[0] == '172':
                continue
            machine.ip = machine.ip.split('.')
            (machine.ip)[0] = '172'
            (machine.ip)[1] = '16'
            machine.ip = '.'.join(machine.ip)
            machine.network = machine.network.split('.')
            (machine.network)[0] = '172'
            (machine.network)[1] = '16'
            machine.network = '.'.join(machine.network)
            machine.subnet = machine.subnet.split('.')
            (machine.subnet)[0] = '172'
            (machine.subnet)[1] = '16'
            machine.subnet = '.'.join(machine.subnet)
            # print machine
    elif cidr == '192.168.0.0':
        for machine in machines:
            if machine.network.split('.')[0] == '192':
                continue
            machine.ip = machine.ip.split('.')
            machine.ip[0] = '192'
            (machine.ip)[1] = '168'
            machine.ip = '.'.join(machine.ip)
            machine.network = machine.network.split('.')
            (machine.network)[0] = '192'
            (machine.network)[1] = '168'
            machine.network = '.'.join(machine.network)
            machine.subnet = machine.subnet.split('.')
            (machine.subnet)[0] = '192'
            (machine.subnet)[1] = '168'
            machine.subnet = '.'.join(machine.subnet)
            # print machine
    else:
        return machines, False
    return machines, True


def update_blueprint(machines, p, db):
    for machine in machines:
        # ram = conv_KB(machine.ram.split(' ')[0])
        # machine.machine_type = '' #compu( machine_type, int(machine['cores']), ram)
        try:
            blprnt = Blueprint(host=machine.host, ip=machine.ip, subnet=machine.subnet, network=machine.network, project=p,
                         ports=machine.ports, cores=machine.cores, public_route=True, cpu_model=machine.cpu_model, ram=machine.ram, machine_type='', status='Not started')
            db.add(blprnt)
            db.commit()
            db.refresh(blprnt)
        except Exception as e:
            print("Boss you have to see this!!")
            print(e)
            return False
    return True


def create_nw_layout(cidr, p, db):
    blueprint_updated = True

    network_cidr_updated = update_nw_cidr(p, db)
    if network_cidr_updated:
        machines, subnet_updated = update_subnet(cidr, p, db)
        if subnet_updated:
            blueprint_updated = update_blueprint(machines, p, db)
        else:
            print("subnet not updated")
            return subnet_updated
    return blueprint_updated


def create_nw(project, name,cidr, db):
    provider = (db.query(Project).filter(Project.name==project).first()).provider
    try:
        if provider == 'gcp':
            ntwrk = Network(project=project, nw_name=name)
            db.add(ntwrk)
            db.commit()
            db.refresh(ntwrk)
        else:
            ntwrk = Network(project=project, nw_name=name, cidr=cidr)
            db.add(ntwrk)
            db.commit()
            db.refresh(ntwrk)
        return True
    except Exception as e:
        print(str(e))
        return False
    

def delete_nw(project, name, db):
    try:
        db.execute(delete(Network).where(
                Network.project==project
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        subnets = db.query(Subnet).filter(Subnet.project==project, Subnet.nw_name==name).all()
        for subnet in subnets:
            db.execute(delete(Subnet).where(
                Subnet.project==project and Subnet.subnet_name==subnet.subnet_name and Subnet.cidr==subnet.cidr
            ).execution_options(synchronize_session="fetch"))
            db.commit()
        return True
    except Exception as e:
        print(str(e))
        return False
    

def delete_subnet(project, name, nw_name, db):
    try:
        cidr = (db.query(Subnet).filter(Subnet.project==project, Subnet.subnet_name==name).first()).cidr
        db.execute(delete(Subnet).where(
                Subnet.project==project and Subnet.subnet_name==name and Subnet.nw_name==nw_name and Subnet.cidr==cidr
            ).execution_options(synchronize_session="fetch"))
        db.commit()
        return True
    except Exception as e:
        print(str(e))
        return False


def fetch_nw(project, db):
    try:
        result = db.query(Network).filter(Network.project==project).all()
        return result
    except Exception as e:
        result = {"msg": "Failed to retrieve network details"}
        return result


def fetch_subnet(project, network, db):
    try:
        if network == 'all':
            result = db.query(Subnet).filter(Subnet.project==project).all()
        else:
            result = db.query(Subnet).filter(Subnet.project==project, Subnet.nw_name==network).all()
        return result
    except Exception as e:
        result = {"msg": "Failed to retrieve network details"}
        return result


def create_subnet(cidr, nw_name, project, subnet_type, name, db):
    try:
        if subnet_type == 'Public':
            subnet_type = True
        elif subnet_type == 'Private':
            subnet_type = False
        
        sbnt = Subnet(project=project, subnet_name=name, cidr=cidr, nw_name=nw_name, subnet_type=subnet_type)
        db.add(sbnt)
        db.commit()
        db.refresh(sbnt)

        if db.query(Subnet).filter(Subnet.project==project).count() == 1:
            nw = db.query(Network).filter(Network.project==project, Network.nw_name==nw_name).first()
            machines = db.query(Discover).filter(Discover.project==project).all()
            for machine in machines:
                try:
                    network_cidr= nw.nw_name if nw.cidr == None else nw.cidr
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==machine.host
                        ).values(
                        ip='Not created', subnet=cidr, network=network_cidr, ports=machine.ports, cores=str(machine.cores), public_route=subnet_type, cpu_model=machine.cpu_model, ram=str(machine.ram), machine_type='', status='0'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()
                except Exception as e:
                    print("Error while updating Blueprint: " + repr(e))
            return True       
        else:
            return True
    except Exception as e:
        print("Error while updating Subnet: " + str(e))
        return False
