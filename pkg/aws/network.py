from mongoengine import *
from model.blueprint import *
import boto3
from utils.dbconn import *

def build_vpc(cidr,public_route, project):
  ec2 = boto3.resource('ec2')
  vpc = ec2.create_vpc(CidrBlock=cidr)
  #vpc.create_tags(Tags=[{"Key": "Name", "Value": "default_vpc"}])
  vpc.wait_until_available()
  try:
    con = create_db_con()
    BluePrint.objects(network=cidr, project=project).update(vpc_id = vpc.id, status='43')
    if public_route:
      ig = ec2.create_internet_gateway()
      vpc.attach_internet_gateway(InternetGatewayId=ig.id)
      BluePrint.objects(network=cidr, project=project).update(ig_id=ig.id)
      route_table = vpc.create_route_table()
      route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=ig.id)
      BluePrint.objects(network=cidr, project=project).update(route_table=route_table.id)
    con.close()
  except Exception as e:
    print(repr(e))
    return False,0
  finally:
    con.close()
  return True, vpc.id

def build_subnet(cidr,vpcid,route,project):
    ec2 = boto3.resource('ec2')
    route_table = ec2.RouteTable(route)
    subnet = ec2.create_subnet(CidrBlock=cidr, VpcId=vpcid)
    try:
      con = create_db_con()
      BluePrint.objects(subnet=cidr, vpc_id=vpcid, project=project).update(subnet_id=subnet.id, status='60')
      route_table.associate_with_subnet(SubnetId=subnet.id)
      con.close()
    except Exception as e:
      print(repr(e))
      return False
    finally:
      con.close()
    return True


async def create_nw(project):
  try:
    con = create_db_con()
    hosts = BluePrint.objects(project=project)
    for host in hosts:
      vpc_id = ''
      if not host['vpc_id']:
        network = BluePrint.objects(project=project, network = host['network'], vpc_id__exists = True)
        if len(network) > 0:
          BluePrint.objects(project=project, network=host['network']).update(vpc_id = network[0]['vpc_id'], status='43')
          subnet = BluePrint.objects(project=project, network = host['network'], subnet = host['subnet'], subnet_id__exists = True)
          if len(subnet) > 0:
            BluePrint.objects(project=project, network=host['network'], subnet=host['subnet']).update(subnet_id = subnet[0]['subnet_id'],status='60')
          else:
            subnet_build = build_subnet(host['subnet'],network[0]['vpc_id']),host['public_route'])
        else:
          vpc_build,vpc_id = build_vpc(host['network'],host['public_route'], project)
          if vpc_build: 
            subnet_build = build_subnet(host['subnet'],vpc_id,host['public_route'], project)
      else:
        if not host['subnet_id']:
          subnet_build = build_subnet(host['subnet'],vpc_id,host['public_route'], project)
  except Exception as e:
    print(repr(e))
    return False
  finally:
    con.close()
  return True