from mongoengine import *
from model.blueprint import *
import boto3
from utils.dbconn import *
import asyncio

async def create_machine(subnet_id,ami_id,machine_type):
    con = create_db_con()
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')
    amiid = ami_id
    filters = [{'Name':'name','Values':[ami_id]}]
    response = client.describe_images(Filters=filters)
    ami_id = response['Images'][0]['ImageId']
    BluePrint.objects(ami_id=amiid).update(status='95')
    instances = ec2.create_instances(ImageId=ami_id, InstanceType=machine_type, MaxCount=1, MinCount=1, NetworkInterfaces=[{'SubnetId': subnet_id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True}])
    instances[0].wait_until_running()
    try:
        BluePrint.objects(ami_id=amiid).update(instance_id=instances[0].id)
        BluePrint.objects(ami_id=amiid).update(status='100')
    except Exception as e:
        print(repr(e))
    finally:
        con.close()


async def build_ec2(project):
    try:
        con = create_db_con()
        hosts = BluePrint.objects(project=project)
        for host in hosts:
            asyncio.create_task(create_machine(host['subnet_id'],host['image_id'],host['machine_type']))
        con.close()
    except Exception as e:
        print(repr(e))
        return False
    finally:
        con.close()
        return True