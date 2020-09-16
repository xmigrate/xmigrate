from mongoengine import *
from model.blueprint import *
import boto3
from utils.dbconn import *

def build_vpc(cidr,public_route):
  ec2 = boto3.resource('ec2')
  vpc = ec2.create_vpc(CidrBlock=cidr)
  #vpc.create_tags(Tags=[{"Key": "Name", "Value": "default_vpc"}])
  vpc.wait_until_available()
  try:
    con = create_db_con()
    BluePrint.objects(network=cidr).update(vpc_id = vpc.id)
    if public_route:
      ig = ec2.create_internet_gateway()
      vpc.attach_internet_gateway(InternetGatewayId=ig.id)
      BluePrint.objects(network=cidr).update(ig_id=ig.id)
      route_table = vpc.create_route_table()
      route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0',GatewayId=ig.id)
      BluePrint.objects(network=cidr).update(route_table=route_table.id)
    con.close()
  except Exception as e:
    print(repr(e))
  finally:
    con.close()

def build_subnet(cidr,vpcid,route):
    ec2 = boto3.resource('ec2')
    route_table = ec2.RouteTable(route)
    subnet = ec2.create_subnet(CidrBlock=cidr, VpcId=vpcid)
    try:
      con = create_db_con()
      BluePrint.objects(subnet=cidr).update(subnet_id=subnet.id)
      route_table.associate_with_subnet(SubnetId=subnet.id)
      con.close()
    except Exception as e:
      print(repr(e))
    finally:
      con.close()
