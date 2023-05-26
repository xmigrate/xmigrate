from model.blueprint import Blueprint
from model.discover import Discover
from model.network import Network, Subnet
from model.project import Project
from sqlalchemy import update, delete


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
                Network.project==project, Network.nw_name==name
            ).execution_options(synchronize_session="fetch"))
        db.commit()

        db.execute(update(Blueprint).where(
            Blueprint.project==project
            ).values(
            vpc_id=None, route_table=None, ig_id=None, subnet_id=None, nic_id=None, ip_created=False
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

        db.execute(update(Blueprint).where(
            Blueprint.project==project
            ).values(
            subnet_id=None, nic_id=None, ip_created=False
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
