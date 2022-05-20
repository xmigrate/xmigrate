from mongoengine import *
from model.blueprint import *
from model.project import *
import boto3
from utils.dbconn import *
import asyncio
from model.network import *
from cassandra.cqlengine.statements import IsNotNull


def build_vpc(cidr,public_route, project):
  con = create_db_con()
  created = Network.objects(cidr=cidr, project=project).allow_filtering()[0]['created']
  if not created:
    access_key = Project.objects(name=project).allow_filtering()[0]['access_key']
    secret_key = Project.objects(name=project).allow_filtering()[0]['secret_key']
    location = Project.objects(name=project).allow_filtering()[0]['location']
    con.shutdown()
    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=location)
    ec2 = session.resource('ec2')
    vpc = ec2.create_vpc(CidrBlock=cidr)
    #vpc.create_tags(Tags=[{"Key": "Name", "Value": "default_vpc"}])
    vpc.wait_until_available()
    try:
      print(vpc)
      con = create_db_con()
      hosts = [x['host'] for x in BluePrint.objects(network=cidr).filter(project=project).allow_filtering()]
      for host in hosts:
        BluePrint.objects(project=project, host=host).update(vpc_id = vpc.id, status='5')
        if public_route:
          ig = ec2.create_internet_gateway()
          vpc.attach_internet_gateway(InternetGatewayId=ig.id)
          BluePrint.objects(project=project, host=host).update(ig_id=ig.id)
          route_table = vpc.create_route_table()
          route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=ig.id)
          BluePrint.objects(project=project, host=host).update(route_table=route_table.id)
          nw_name = Network.objects(cidr=cidr, project=project).allow_filtering()[0]['nw_name']
          Network.objects(cidr=cidr, project=project, nw_name=nw_name).update(created=True)
      con.shutdown()
    except Exception as e:
      print(repr(e))
      return False,0
    finally:
      con.shutdown()
    return True, vpc.id
  else:
    return True


def build_subnet(cidr,vpcid,route,project):
    con = create_db_con()
    created = Subnet.objects(cidr=cidr, project=project).allow_filtering()[0]['created']
    if not created:
      access_key = Project.objects(name=project).allow_filtering()[0]['access_key']
      secret_key = Project.objects(name=project).allow_filtering()[0]['secret_key']
      location = Project.objects(name=project).allow_filtering()[0]['location']
      con.shutdown()
      session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=location)
      ec2 = session.resource('ec2')
      route_table = ec2.RouteTable(route)
      subnet = ec2.create_subnet(CidrBlock=cidr, VpcId=vpcid)
      try:
        print(subnet)
        con = create_db_con()
        hosts = [x['host'] for x in BluePrint.objects(subnet=cidr, vpc_id=vpcid, project=project).allow_filtering()]
        print(hosts)
        for host in hosts:
          BluePrint.objects(project=project, host=host).update(subnet_id=subnet.id, status='20')
          subnet_name = Subnet.objects(cidr=cidr, project=project).allow_filtering()[0]['subnet_name']
          Subnet.objects(cidr=cidr, project=project, subnet_name=subnet_name).update(created=True)
          route_table.associate_with_subnet(SubnetId=subnet.id)
        con.shutdown()
      except Exception as e:
        print(repr(e))
        return False
      finally:
        con.shutdown()
      return True
    else:
      return True


async def create_nw(project):
  try:
    con = create_db_con()
    hosts = BluePrint.objects(project=project).allow_filtering()
    for host in hosts:
      vpc_id = ''
      if not host['vpc_id']:
        print("hi")
        all_networks = [dict(x) for x in BluePrint.objects(project=project, network = host['network']).allow_filtering()]
        network = []
        for i in all_networks:
          if i['vpc_id'] != None:
            network.append(i)
        if len(network) > 0:
          BluePrint.objects(project=project, network=host['network']).update(vpc_id = network[0]['vpc_id'], status='5')
          all_subnet = [ dict(x) for x in BluePrint.objects(project=project, network = host['network'], subnet = host['subnet']).allow_filtering() ]
          subnet = []
          for i in all_subnet:
            if subnet['subnet_id'] != None:
              subnet.append(i)
          if len(subnet) > 0:
            BluePrint.objects(project=project, network=host['network'], subnet=host['subnet']).update(subnet_id = subnet[0]['subnet_id'],status='20')
          else:
            updated_host = BluePrint.objects(project=project, network=host['network'], host=host['host']).allow_filtering()[0]
            subnet_build = build_subnet(updated_host['subnet'],updated_host['vpc_id'],updated_host['route_table'], project)
        else:
          vpc_build,vpc_id = build_vpc(host['network'],host['public_route'], project)
          if vpc_build:
            updated_host = BluePrint.objects(project=project, network=host['network'], host=host['host']).allow_filtering()[0]
            subnet_build = build_subnet(host['subnet'],vpc_id,updated_host['route_table'], project)
      else:
        if not host['subnet_id']:
          updated_host = BluePrint.objects(project=project, network=host['network'], host=host['host']).allow_filtering()[0]
          subnet_build = build_subnet(host['subnet'],updated_host['vpc_id'],updated_host['route_table'], project)
  except Exception as e:
    print(repr(e))
    return False
  finally:
    con.shutdown()
  return True