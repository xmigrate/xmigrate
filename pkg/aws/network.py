from schemas.machines import VMUpdate
from schemas.network import NetworkUpdate, SubnetUpdate
from services.blueprint import get_blueprintid
from services.machines import get_all_machines, update_vm
from services.network import get_all_networks, get_all_subnets, update_network, update_subnet
from services.project import get_projectid, get_project_by_name
from utils.logger import Logger
import boto3


def build_vpc(machine_id, network, public_route, project, update_host, db):
    try:
        session = boto3.Session(aws_access_key_id=project.aws_access_key, aws_secret_access_key=project.aws_secret_key, region_name=project.location)
        ec2 = session.resource('ec2')
        Logger.info('Provisioning VPC...')
        vpc = ec2.create_vpc(CidrBlock=network.cidr)
        vpc.create_tags(Tags=[{"Key": "Name", "Value": network.name}])
        vpc.wait_until_available()

        network_data = NetworkUpdate(network_id=network.id, target_network_id=vpc.id, created=True)
        update_network(network_data, db)

        if update_host:
            vm_data = VMUpdate(machine_id=machine_id, status=5)
            update_vm(vm_data, db)
        
        Logger.info('VPC created with id %s' %(vpc.id))

        if public_route:
            ig = ec2.create_internet_gateway()
            vpc.attach_internet_gateway(InternetGatewayId=ig.id)

            route_table = vpc.create_route_table()
            route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=ig.id)
            network_data = NetworkUpdate(network_id=network.id, ig_id=ig.id, route_table=route_table.id)
            update_network(network_data, db)

            Logger.info('Internet Gateway created with id %s' %(ig.id))
        return True, vpc.id
    except Exception as e:
        Logger.error(str(e))
        return False, None


def build_subnet(machine_id, subnet_data, vpc_id, route, project, update_host, db):
    try:   
        session = boto3.Session(aws_access_key_id=project.aws_access_key, aws_secret_access_key=project.aws_secret_key, region_name=project.location)
        ec2 = session.resource('ec2')
        route_table = ec2.RouteTable(route)
        Logger.info('Provisioning subnet...')
        subnet = ec2.create_subnet(CidrBlock=subnet_data.cidr, VpcId=vpc_id)
        subnet.create_tags(Tags=[{"Key": "Name", "Value": subnet_data.subnet_name}])
        route_table.associate_with_subnet(SubnetId=subnet.id)

        subnet_data = SubnetUpdate(subnet_id=subnet_data.id, target_subnet_id=subnet.id, created=True)
        update_subnet(subnet_data, db)

        if update_host:
            vm_data = VMUpdate(machine_id=machine_id, status=20)
            update_vm(vm_data, db)

        Logger.info('Subnet created with id %s' %(subnet.id))
    except Exception as e:
        Logger.error(str(e))


async def create_nw(user, project, db) -> bool:
    Logger.info("Starting migration, some operations might take few minutes...")
    try:
        project_id = get_projectid(user, project, db)
        blueprint_id = get_blueprintid(project_id, db)
        project = get_project_by_name(user, project, db)
        hosts = get_all_machines(blueprint_id, db)
        for host in hosts:
            networks = get_all_networks(blueprint_id, db)
            for network in networks:
                vpc_id = network.target_network_id
                vpc_created = network.created
                subnets = get_all_subnets(network.id, db)
                update_host = True if network.cidr == host.network else False
                if vpc_id is None and not network.created:
                    vpc_created, vpc_id = build_vpc(host.id, network, host.public_route, project, update_host, db)
                for subnet in subnets:
                    if not subnet.created and vpc_created:
                        build_subnet(host.id, subnet, vpc_id, network.route_table, project, update_host, db)
        return True
    except Exception as e:
        Logger.error(str(e))
        return False