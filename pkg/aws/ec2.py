from mongoengine import *
from model.blueprint import *
import boto3
from utils.dbconn import *
import asyncio
from model.project import *
from pkg.aws import creds

async def create_machine(project,subnet_id,ami_id,machine_type):
    con = create_db_con()
    access_key = Project.objects(name=project)[0]['access_key']
    secret_key = Project.objects(name=project)[0]['secret_key']
    location = Project.objects(name=project)[0]['location']
    con.close()
    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=location)
    ec2 = session.resource('ec2')
    client = boto3.client('ec2',aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=location)
    amiid = ami_id
    filters = [{'Name':'name','Values':[ami_id]}]
    response = client.describe_images(Filters=filters)
    ami_id = response['Images'][0]['ImageId']
    BluePrint.objects(image_id=amiid).update(status='95')
    instances = ec2.create_instances(ImageId=ami_id, InstanceType=machine_type, MaxCount=1, MinCount=1, NetworkInterfaces=[{'SubnetId': subnet_id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True}])
    instances[0].wait_until_running()
    instance_id = instances[0].id
    running_instances = ec2.instances.filter(InstanceIds=[instance_id])
    ip = ''
    for instance in running_instances:
        ip = instance.public_ip_address
    try:
        BluePrint.objects(image_id=amiid).update(vm_id=instances[0].id, ip=ip)
        BluePrint.objects(image_id=amiid).update(status='100')
    except Exception as e:
        print(repr(e))
    finally:
        con.close()


async def build_ec2(project):
    try:
        print(project)
        con = create_db_con()
        hosts = BluePrint.objects(project=project)
        for host in hosts:
            print(host['machine_type'])
            await create_machine(project,host['subnet_id'],host['image_id'],host['machine_type'])
        con.close()
        return True
    except Exception as e:
        print(str(e))
        print(repr(e))
        return False
    finally:
        con.close()


def ec2_instance_types(ec2,region_name):
    describe_args = {}
    while True:
        describe_result = ec2.describe_instance_types(**describe_args)
        yield from [i for i in describe_result['InstanceTypes']]
        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']



def get_vm_types(project):
    location = ''
    machine_types = []
    try:
        con = create_db_con()
        access_key = Project.objects(name=project)[0]['access_key']
        secret_key = Project.objects(name=project)[0]['secret_key']
        location = Project.objects(name=project)[0]['location']
        client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,region_name=location)
        for ec2_type in ec2_instance_types(client,location):
            print(ec2_type)
            cores = ''
            if 'DefaultCores' in ec2_type['VCpuInfo'].keys():
                cores = ec2_type['VCpuInfo']['DefaultCores']
            else:
                cores = str(ec2_type['VCpuInfo']['DefaultVCpus'])+'_vcpus'
            machine_types.append({"vm_name":ec2_type['InstanceType'],"cores":cores,"memory":ec2_type['MemoryInfo']['SizeInMiB']})
        flag = True
    except Exception as e:
        print(repr(e))
        logger(str(e),"warning")

        flag = False
    finally:
        con.close()
    return machine_types, flag