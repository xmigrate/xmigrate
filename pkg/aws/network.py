from model.blueprint import Blueprint
from model.network import Network, Subnet
from model.project import Project
import boto3
from sqlalchemy import update


def build_vpc(cidr, public_route, project, db):
    created = (db.query(Network).filter(Network.cidr==cidr, Network.project==project).first()).created
    if not created:
        prjct = db.query(Project).filter(Project.name==project).first()
        session = boto3.Session(aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key, region_name=prjct.location)
        ec2 = session.resource('ec2')
        print('Provisioning VPC...')
        vpc = ec2.create_vpc(CidrBlock=cidr)
        #vpc.create_tags(Tags=[{"Key": "Name", "Value": "default_vpc"}])
        vpc.wait_until_available()
        try:
            hosts = [blprnt.host for blprnt in db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==cidr).all()]
            for host in hosts:
                db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host
                        ).values(
                        vpc_id=vpc.id, status='5'
                        ).execution_options(synchronize_session="fetch"))
                db.commit()

                nw_name = (db.query(Network).filter(Network.project==project, Network.cidr==cidr).first()).nw_name

                db.execute(update(Network).where(
                    Network.project==project and Network.nw_name==nw_name and Network.cidr==cidr
                    ).values(
                    vpc_id=vpc.id, created=True
                    ).execution_options(synchronize_session="fetch"))
                db.commit()

                if public_route:
                    ig = ec2.create_internet_gateway()
                    vpc.attach_internet_gateway(InternetGatewayId=ig.id)

                    route_table = vpc.create_route_table()
                    route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=ig.id)

                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host
                        ).values(
                        ig_id=ig.id, route_table=route_table.id
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    db.execute(update(Network).where(
                        Network.project==project and Network.nw_name==nw_name and Network.cidr==cidr
                        ).values(
                        ig_id=ig.id, route_table=route_table.id
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()
        except Exception as e:
            print(repr(e))
            return False, 0
        print(f'VPC created with id {vpc.id}.')
        return True, vpc.id
    else:
        return True, None


def build_subnet(cidr, vpcid, route, project, db):
    created = (db.query(Subnet).filter(Subnet.project==project, Subnet.cidr==cidr).first()).created
    if not created:
        prjct = db.query(Project).filter(Project.name==project).first()
        session = boto3.Session(aws_access_key_id=prjct.access_key, aws_secret_access_key=prjct.secret_key, region_name=prjct.location)
        ec2 = session.resource('ec2')
        route_table = ec2.RouteTable(route)
        print('Provisioning subnet...')
        subnet = ec2.create_subnet(CidrBlock=cidr, VpcId=vpcid)
        try:
            hosts = [blprnt.host for blprnt in db.query(Blueprint).filter(Blueprint.project==project, Blueprint.subnet==cidr, Blueprint.vpc_id==vpcid).all()]
            
            for host in hosts:
                db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.host==host
                        ).values(
                        subnet_id=subnet.id, status='20'
                        ).execution_options(synchronize_session="fetch"))
                db.commit()

                subnet_name = (db.query(Subnet).filter(Subnet.project==project, Subnet.cidr==cidr).first()).subnet_name

                db.execute(update(Subnet).where(
                        Subnet.project==project and Subnet.cidr==cidr and Subnet.subnet_name==subnet_name
                        ).values(
                        created=True
                        ).execution_options(synchronize_session="fetch"))
                db.commit()

                route_table.associate_with_subnet(SubnetId=subnet.id)
        except Exception as e:
            print(repr(e))
            return False
        print(f'Subnet created with id {subnet.id}.')
        return True
    else:
      return True


async def create_nw(project, db):
    try:
        hosts = db.query(Blueprint).filter(Blueprint.project==project).all()
        for host in hosts:
            vpc_id = ''
            if host.vpc_id is None:
                all_networks = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==host.network).all()
                network = []

                for i in all_networks:
                    if i.vpc_id is not None:
                        network.append(i)

                if len(network) > 0:
                    db.execute(update(Blueprint).where(
                        Blueprint.project==project and Blueprint.network==host.network
                        ).values(
                        vpc_id=(network[0]).vpc_id, status='5'
                        ).execution_options(synchronize_session="fetch"))
                    db.commit()

                    all_subnet = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==host.network, Blueprint.subnet==host.subnet).all()
                    subnet = []

                    for i in all_subnet:
                        if i.subnet_id is not None:
                            subnet.append(i)

                    if len(subnet) > 0:
                        db.execute(update(Blueprint).where(
                            Blueprint.project==project and Blueprint.network==host.network and Blueprint.subnet==host.subnet
                            ).values(
                            subnet_id=(subnet[0]).subnet_id, status='20'
                            ).execution_options(synchronize_session="fetch"))
                        db.commit()
                    else:
                        updated_host = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==host.network, Blueprint.host==host.host).first()
                        build_subnet(updated_host.subnet, updated_host.vpc_id, updated_host.route_table, project)
                else:
                    vpc_build, vpc_id = build_vpc(host.network, host.public_route, project, db)
                    if vpc_build:
                        updated_host = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==host.network, Blueprint.host==host.host).first()
                        build_subnet(host.subnet, vpc_id, updated_host.route_table, project, db)
            else:
                if host.subnet_id is None:
                    updated_host = db.query(Blueprint).filter(Blueprint.project==project, Blueprint.network==host.network, Blueprint.host==host.host).first()
                    build_subnet(host.subnet, updated_host.vpc_id, updated_host.route_table, project, db)
    except Exception as e:
        print(repr(e))
        return False
    return True